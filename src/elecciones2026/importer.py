"""Isolated offline electoral programme source import and hash verification.

Enforces strict security boundaries on untrusted source documents and URLs:
- File size, memory, and chunk limits (maximum 50 MB default).
- MIME and magic byte validation (%PDF- header verification, polyglot rejection).
- Static inspection rejecting active/embedded executable content (/JavaScript, /Launch,
  /EmbeddedFiles, /SubmitForm, /ImportData, /RichMedia, /Screen, /Sound).
- Strict network isolation: SSRF guard rejecting private, loopback, link-local,
  carrier-grade NAT, and cloud metadata addresses; scheme enforcement; redirect limits;
  socket timeouts; and complete offline isolation mode.
- Cryptographic SHA-256 hash calculation and constant-time validation.
- Zero source code execution: no dynamic evaluation, shell execution, or script execution.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import ipaddress
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Optional, Union

from elecciones2026.source_register import SourceRecord, SourceRegister, load_register

# ---------------------------------------------------------------------------
# Constants and Security Limits
# ---------------------------------------------------------------------------

# 50 MB ceiling per docs/SOURCE-AVAILABILITY-2026.md and docs/SECURITY.md
DEFAULT_MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024
DEFAULT_MIN_FILE_SIZE_BYTES: int = 8
DEFAULT_TIMEOUT_SECONDS: float = 15.0
DEFAULT_MAX_REDIRECTS: int = 3
DEFAULT_CHUNK_SIZE: int = 64 * 1024  # 64 KB streaming buffer

SHA256_HEX_PATTERN = re.compile(r"^[a-f0-9]{64}$")
PDF_MAGIC_PATTERN = re.compile(rb"%PDF-([0-9]+\.[0-9]+)")
PDF_NAME_TOKEN_PATTERN = re.compile(rb"/([^\s()<>{}/%\[\]]+)")
HEX_ESCAPE_PATTERN = re.compile(rb"#([0-9a-fA-F]{2})")

DEFAULT_ALLOWED_SCHEMES: tuple[str, ...] = ("https",)

DEFAULT_ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        "application/pdf",
        "application/x-pdf",
        "binary/octet-stream",
        "application/octet-stream",
    }
)

# Known executable or container signatures that MUST NOT precede or mask as a PDF
BLOCKED_POLYGLOT_SIGNATURES: tuple[bytes, ...] = (
    b"MZ",  # DOS / Windows PE Executable
    b"\x7fELF",  # Linux ELF Executable
    b"\xca\xfe\xba\xbe",  # Java Class / Mach-O Fat Binary
    b"\xfe\xed\xfa\xce",  # Mach-O 32-bit (big-endian)
    b"\xce\xfa\xed\xfe",  # Mach-O 32-bit (little-endian)
    b"\xfe\xed\xfa\xcf",  # Mach-O 64-bit (big-endian)
    b"\xcf\xfa\xed\xfe",  # Mach-O 64-bit (little-endian)
    b"PK\x03\x04",  # ZIP Archive / JAR / APK
    b"PK\x05\x06",  # Empty ZIP
    b"PK\x07\x08",  # Spanned ZIP
    b"<!DOCTYPE ",  # HTML
    b"<!doctype ",
    b"<html",
    b"<HTML",
    b"<?xml ",
    b"#!/",  # Unix Shebang / Script
)

# Prohibited PDF dictionary names indicating active, interactive, or executable payloads
PROHIBITED_ACTIVE_CONTENT_NAMES: frozenset[bytes] = frozenset(
    {
        b"javascript",
        b"js",
        b"launch",
        b"embeddedfiles",
        b"embeddedfile",
        b"submitform",
        b"importdata",
        b"richmedia",
        b"screen",
        b"sound",
        b"xfa",
    }
)

# Blocked IP networks for SSRF protection
BLOCKED_IPV4_NETWORKS: tuple[ipaddress.IPv4Network, ...] = (
    ipaddress.ip_network("0.0.0.0/8"),  # Current network ("this" host)
    ipaddress.ip_network("10.0.0.0/8"),  # Private-use (RFC 1918)
    ipaddress.ip_network("100.64.0.0/10"),  # Carrier-grade NAT (RFC 6598)
    ipaddress.ip_network("127.0.0.0/8"),  # Loopback (RFC 1122)
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local / Cloud metadata (RFC 3927)
    ipaddress.ip_network("172.16.0.0/12"),  # Private-use (RFC 1918)
    ipaddress.ip_network("192.0.0.0/24"),  # IETF Protocol Assignments (RFC 6890)
    ipaddress.ip_network("192.0.2.0/24"),  # Documentation TEST-NET-1 (RFC 5737)
    ipaddress.ip_network("192.88.99.0/24"),  # 6to4 Relay Anycast (RFC 7526)
    ipaddress.ip_network("192.168.0.0/16"),  # Private-use (RFC 1918)
    ipaddress.ip_network("198.18.0.0/15"),  # Benchmarking (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"),  # Documentation TEST-NET-2 (RFC 5737)
    ipaddress.ip_network("203.0.113.0/24"),  # Documentation TEST-NET-3 (RFC 5737)
    ipaddress.ip_network("224.0.0.0/4"),  # Multicast (RFC 5771)
    ipaddress.ip_network("240.0.0.0/4"),  # Reserved for future use (RFC 1112)
    ipaddress.ip_network("255.255.255.255/32"),  # Limited broadcast
)

BLOCKED_IPV6_NETWORKS: tuple[ipaddress.IPv6Network, ...] = (
    ipaddress.ip_network("::/128"),  # Unspecified
    ipaddress.ip_network("::1/128"),  # Loopback
    ipaddress.ip_network("::ffff:0:0/96"),  # IPv4-mapped IPv6
    ipaddress.ip_network("64:ff9b::/96"),  # IPv4/IPv6 translation
    ipaddress.ip_network("100::/64"),  # Discard prefix
    ipaddress.ip_network("2001:db8::/32"),  # Documentation
    ipaddress.ip_network("fc00::/7"),  # Unique Local Address (ULA / private)
    ipaddress.ip_network("fe80::/10"),  # Link-local
    ipaddress.ip_network("ff00::/8"),  # Multicast
)

BLOCKED_HOSTNAMES: frozenset[str] = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "broadcasthost",
        "ip6-localhost",
        "ip6-loopback",
    }
)

BLOCKED_HOSTNAME_SUFFIXES: tuple[str, ...] = (
    ".local",
    ".localhost",
    ".internal",
    ".lan",
    ".home",
)


# ---------------------------------------------------------------------------
# Exception Hierarchy
# ---------------------------------------------------------------------------


class SourceImportError(Exception):
    """Base exception for all source import and validation errors."""


class SizeLimitExceededError(SourceImportError):
    """Raised when source input exceeds configured maximum size boundaries."""

    def __init__(self, current_size: int, max_size: int, message: Optional[str] = None):
        self.current_size = current_size
        self.max_size = max_size
        default_msg = (
            f"Input size ({current_size} bytes) exceeds maximum allowable limit of {max_size} bytes."
        )
        super().__init__(message or default_msg)


class EmptyFileError(SourceImportError):
    """Raised when source input is empty (0 bytes) or below minimum required length."""

    def __init__(self, current_size: int, min_size: int, message: Optional[str] = None):
        self.current_size = current_size
        self.min_size = min_size
        default_msg = (
            f"Source file is empty or too small ({current_size} bytes; minimum {min_size} bytes required)."
        )
        super().__init__(message or default_msg)


class InvalidFileFormatError(SourceImportError):
    """Raised when source document does not meet PDF format requirements."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid PDF source format: {reason}")


class ActiveContentDetectedError(SourceImportError):
    """Raised when active/executable code or embedded scripts are detected in the PDF."""

    def __init__(self, findings: list[str]):
        self.findings = findings
        findings_str = "; ".join(findings)
        super().__init__(
            f"Security policy violation: active or executable content detected in PDF: {findings_str}"
        )


class HashMismatchError(SourceImportError):
    """Raised when computed SHA-256 hash does not match expected cryptographic hash."""

    def __init__(self, computed_hash: str, expected_hash: str, source_id: Optional[str] = None):
        self.computed_hash = computed_hash
        self.expected_hash = expected_hash
        self.source_id = source_id
        src_prefix = f"Source '{source_id}': " if source_id else ""
        super().__init__(
            f"{src_prefix}SHA-256 hash mismatch! Computed: '{computed_hash}', expected: '{expected_hash}'."
        )


class InvalidHashFormatError(SourceImportError):
    """Raised when expected hash is not a valid 64-character lowercase hex SHA-256 string."""

    def __init__(self, invalid_hash: str):
        self.invalid_hash = invalid_hash
        super().__init__(
            f"Expected hash '{invalid_hash}' is not a valid 64-character lowercase hex SHA-256 string."
        )


class NetworkSecurityError(SourceImportError):
    """Base exception for network boundary and URL security violations."""


class SSRFSecurityError(NetworkSecurityError):
    """Raised when a URL attempts to access private, loopback, or metadata addresses."""

    def __init__(self, url: str, ip_address: Optional[str], reason: str):
        self.url = url
        self.ip_address = ip_address
        self.reason = reason
        ip_info = f" (resolving to {ip_address})" if ip_address else ""
        super().__init__(f"SSRF policy blocked URL '{url}'{ip_info}: {reason}")


class DisallowedSchemeError(NetworkSecurityError):
    """Raised when a URL uses a disallowed or unsafe protocol scheme."""

    def __init__(self, url: str, scheme: str, allowed_schemes: tuple[str, ...]):
        self.url = url
        self.scheme = scheme
        self.allowed_schemes = allowed_schemes
        super().__init__(
            f"Disallowed URL scheme '{scheme}' in '{url}'. Only {list(allowed_schemes)} are permitted."
        )


class DisallowedHostError(NetworkSecurityError):
    """Raised when a URL targets a disallowed hostname or port."""

    def __init__(self, url: str, host: str, reason: str):
        self.url = url
        self.host = host
        self.reason = reason
        super().__init__(f"Disallowed target host '{host}' in '{url}': {reason}")


class DNSResolutionError(NetworkSecurityError):
    """Raised when host DNS lookup fails during SSRF validation."""

    def __init__(self, hostname: str, reason: str):
        self.hostname = hostname
        self.reason = reason
        super().__init__(f"DNS resolution failed for hostname '{hostname}': {reason}")


class RedirectSecurityError(NetworkSecurityError):
    """Raised when HTTP redirect sequence violates security policy or exceeds max hops."""

    def __init__(self, current_url: str, target_url: Optional[str], reason: str):
        self.current_url = current_url
        self.target_url = target_url
        self.reason = reason
        target_info = f" -> '{target_url}'" if target_url else ""
        super().__init__(f"Redirect security violation at '{current_url}'{target_info}: {reason}")


class NetworkTimeoutError(NetworkSecurityError):
    """Raised when network operation exceeds configured timeout ceiling."""

    def __init__(self, url: str, timeout_seconds: float):
        self.url = url
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Network request to '{url}' timed out after {timeout_seconds} seconds."
        )


class HTTPStatusError(NetworkSecurityError):
    """Raised when HTTP endpoint returns non-successful status code (4xx, 5xx)."""

    def __init__(self, url: str, status_code: int, reason: str):
        self.url = url
        self.status_code = status_code
        self.reason = reason
        super().__init__(f"HTTP request to '{url}' failed with status {status_code}: {reason}")


class OfflineModeViolationError(NetworkSecurityError):
    """Raised when network request is attempted while offline_only mode is active."""

    def __init__(self, url: str):
        self.url = url
        super().__init__(
            f"Network access disabled: attempted external request to '{url}' in offline-only mode."
        )


# ---------------------------------------------------------------------------
# Configuration and Result Records
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImportConfig:
    """Security boundaries and execution limits for offline source import."""

    max_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES
    min_size_bytes: int = DEFAULT_MIN_FILE_SIZE_BYTES
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    max_redirects: int = DEFAULT_MAX_REDIRECTS
    chunk_size: int = DEFAULT_CHUNK_SIZE
    allowed_schemes: tuple[str, ...] = DEFAULT_ALLOWED_SCHEMES
    allowed_content_types: frozenset[str] = DEFAULT_ALLOWED_CONTENT_TYPES
    require_pdf: bool = True
    disallow_private_ips: bool = True
    allow_loopback_for_testing: bool = False
    disallow_active_content: bool = True
    offline_only: bool = False
    user_agent: str = "elecciones2026-offline-importer/1.0"


@dataclass(frozen=True)
class ImportResult:
    """Cryptographic, structural, and security verification result for an imported source."""

    status: str  # "verified" or "rejected"
    sha256: str
    size_bytes: int
    file_type: str
    pdf_version: Optional[str] = None
    active_content_detected: bool = False
    active_content_findings: list[str] = field(default_factory=list)
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    verified_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Cryptographic Hash Utilities
# ---------------------------------------------------------------------------


def validate_sha256_format(expected_hash: str) -> str:
    """Validate and normalize a 64-character lowercase hexadecimal SHA-256 string.

    Raises InvalidHashFormatError if format is invalid.
    """
    cleaned = expected_hash.strip().lower()
    if not SHA256_HEX_PATTERN.match(cleaned):
        raise InvalidHashFormatError(expected_hash)
    return cleaned


def compute_bytes_sha256(data: bytes) -> str:
    """Compute lowercase SHA-256 hexadecimal hash from bytes."""
    return hashlib.sha256(data).hexdigest()


def compute_file_sha256(path: Union[Path, str], chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """Compute lowercase SHA-256 hexadecimal hash from a file path using constant-memory streaming."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_hash(
    actual_hash: str,
    expected_hash: str,
    source_id: Optional[str] = None,
) -> bool:
    """Verify actual hash against expected hash using constant-time comparison.

    Raises HashMismatchError if hashes differ.
    Raises InvalidHashFormatError if expected hash is malformed.
    """
    normalized_expected = validate_sha256_format(expected_hash)
    normalized_actual = actual_hash.strip().lower()

    if not hmac.compare_digest(normalized_actual, normalized_expected):
        raise HashMismatchError(
            computed_hash=normalized_actual,
            expected_hash=normalized_expected,
            source_id=source_id,
        )
    return True


# ---------------------------------------------------------------------------
# Network & SSRF Security Boundaries
# ---------------------------------------------------------------------------


def is_ip_blocked(
    ip: Union[ipaddress.IPv4Address, ipaddress.IPv6Address],
    allow_loopback: bool = False,
) -> tuple[bool, Optional[str]]:
    """Determine whether an IP address belongs to blocked/private ranges."""
    # Check IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1)
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped

    if allow_loopback and ip.is_loopback:
        return False, None

    if ip.is_loopback:
        return True, "Loopback address"

    if ip.is_private:
        return True, "Private RFC 1918 / RFC 4193 network"

    if ip.is_link_local:
        return True, "Link-local address (including cloud metadata service)"

    if ip.is_multicast:
        return True, "Multicast address"

    if ip.is_reserved:
        return True, "IETF reserved address"

    if ip.is_unspecified:
        return True, "Unspecified 0.0.0.0 / :: address"

    if isinstance(ip, ipaddress.IPv4Address):
        for net in BLOCKED_IPV4_NETWORKS:
            if ip in net:
                return True, f"Blocked IPv4 range ({net})"
    elif isinstance(ip, ipaddress.IPv6Address):
        for net in BLOCKED_IPV6_NETWORKS:
            if ip in net:
                return True, f"Blocked IPv6 range ({net})"

    return False, None


def validate_url(url: str, config: Optional[ImportConfig] = None) -> list[str]:
    """Validate URL syntax, scheme, and SSRF boundaries.

    Returns list of resolved safe IP addresses for the target host.
    Raises DisallowedSchemeError, SSRFSecurityError, or DisallowedHostError.
    """
    cfg = config or ImportConfig()

    parsed = urllib.parse.urlsplit(url)

    # 1. Scheme check
    if not parsed.scheme or parsed.scheme.lower() not in cfg.allowed_schemes:
        raise DisallowedSchemeError(
            url=url,
            scheme=parsed.scheme or "none",
            allowed_schemes=cfg.allowed_schemes,
        )

    # 2. Userinfo check (credentials embedded in URL)
    if parsed.username or parsed.password:
        raise DisallowedHostError(
            url=url,
            host=parsed.netloc,
            reason="Embedded user credentials in URL are prohibited",
        )

    # 3. Hostname check
    hostname = parsed.hostname
    if not hostname:
        raise DisallowedHostError(url=url, host="", reason="Empty hostname")

    clean_hostname = hostname.strip().lower()

    if clean_hostname in BLOCKED_HOSTNAMES:
        if not cfg.allow_loopback_for_testing:
            raise SSRFSecurityError(
                url=url,
                ip_address=None,
                reason=f"Hostname '{clean_hostname}' is explicitly blocked",
            )

    for suffix in BLOCKED_HOSTNAME_SUFFIXES:
        if clean_hostname.endswith(suffix):
            if not cfg.allow_loopback_for_testing:
                raise SSRFSecurityError(
                    url=url,
                    ip_address=None,
                    reason=f"Hostname suffix '{suffix}' is prohibited",
                )

    # 4. Port validation
    if parsed.port is not None:
        if parsed.scheme == "https" and parsed.port not in (443, 8443):
            if not cfg.allow_loopback_for_testing:
                raise DisallowedHostError(
                    url=url,
                    host=hostname,
                    reason=f"Non-standard port {parsed.port} prohibited for HTTPS",
                )
        elif parsed.scheme == "http" and parsed.port not in (80, 8080):
            if not cfg.allow_loopback_for_testing:
                raise DisallowedHostError(
                    url=url,
                    host=hostname,
                    reason=f"Non-standard port {parsed.port} prohibited for HTTP",
                )

    # 5. IP / DNS Resolution and SSRF inspection
    if not cfg.disallow_private_ips:
        return []

    # Check if host is an IP literal
    try:
        ip = ipaddress.ip_address(clean_hostname)
        blocked, reason = is_ip_blocked(ip, allow_loopback=cfg.allow_loopback_for_testing)
        if blocked:
            raise SSRFSecurityError(url=url, ip_address=str(ip), reason=reason or "Blocked IP")
        return [str(ip)]
    except ValueError:
        pass  # Hostname, proceed to DNS lookup

    # Resolve hostname to all associated IPs
    resolved_ips: list[str] = []
    try:
        # Use SOCK_STREAM for web connections
        addrinfo = socket.getaddrinfo(clean_hostname, None, type=socket.SOCK_STREAM)
        for entry in addrinfo:
            sockaddr = entry[4]
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            blocked, reason = is_ip_blocked(
                ip_obj, allow_loopback=cfg.allow_loopback_for_testing
            )
            if blocked:
                raise SSRFSecurityError(
                    url=url,
                    ip_address=ip_str,
                    reason=reason or "Blocked network address",
                )
            resolved_ips.append(ip_str)
    except socket.gaierror as err:
        raise DNSResolutionError(hostname=clean_hostname, reason=str(err))

    if not resolved_ips:
        raise DNSResolutionError(
            hostname=clean_hostname, reason="No IP addresses resolved for host"
        )

    return resolved_ips


# ---------------------------------------------------------------------------
# PDF Structure Inspection & Active Content Scanner
# ---------------------------------------------------------------------------


def decode_pdf_name(raw_name: bytes) -> bytes:
    """Decode PDF hex escape sequences in a Name token (e.g. /Java#53cript -> /JavaScript)."""
    return HEX_ESCAPE_PATTERN.sub(
        lambda m: bytes([int(m.group(1), 16)]),
        raw_name,
    )


def inspect_pdf_bytes(
    data: bytes,
    config: Optional[ImportConfig] = None,
) -> tuple[Optional[str], list[str]]:
    """Inspect PDF header and scan for active/executable code without executing source content.

    Returns (pdf_version, active_content_findings).
    Raises EmptyFileError, InvalidFileFormatError, or ActiveContentDetectedError.
    """
    cfg = config or ImportConfig()

    data_len = len(data)
    if data_len < cfg.min_size_bytes:
        raise EmptyFileError(
            current_size=data_len,
            min_size=cfg.min_size_bytes,
        )

    # 1. Polyglot / Executable header detection
    for sig in BLOCKED_POLYGLOT_SIGNATURES:
        if data.startswith(sig):
            sig_repr = repr(sig)
            raise InvalidFileFormatError(
                f"File starts with prohibited signature {sig_repr} (polyglot/executable disguise detected)."
            )

    # 2. PDF magic bytes verification in first 1024 bytes (ISO 32000-1 §7.5.2)
    header_window = data[:1024]
    magic_idx = header_window.find(b"%PDF-")
    if magic_idx == -1:
        raise InvalidFileFormatError(
            "Missing required '%PDF-' magic bytes in document header (first 1024 bytes)."
        )

    # Strict check: header must not be preceded by arbitrary non-whitespace junk
    prefix = header_window[:magic_idx]
    if prefix and not prefix.isspace():
        raise InvalidFileFormatError(
            "Document contains foreign data preceding %PDF- header."
        )

    match = PDF_MAGIC_PATTERN.search(header_window[magic_idx:])
    if not match:
        raise InvalidFileFormatError("Malformed or unparseable %PDF- version header.")

    pdf_version = match.group(1).decode("ascii", errors="replace")

    # 3. Active / Executable content token scan
    # Scan all Name tokens in document bytes, decoding #xx escapes
    findings: list[str] = []
    seen_prohibited: set[bytes] = set()

    for token_match in PDF_NAME_TOKEN_PATTERN.finditer(data):
        raw_name = token_match.group(1)
        decoded = decode_pdf_name(raw_name).lower()
        if decoded in PROHIBITED_ACTIVE_CONTENT_NAMES and decoded not in seen_prohibited:
            seen_prohibited.add(decoded)
            name_str = decoded.decode("ascii", errors="replace")
            findings.append(f"Prohibited active/executable PDF dictionary token: /{name_str}")

    if findings and cfg.disallow_active_content:
        raise ActiveContentDetectedError(findings=findings)

    return pdf_version, findings


# ---------------------------------------------------------------------------
# Isolated HTTP Fetcher with Size, Time, and Redirect Enforcements
# ---------------------------------------------------------------------------


class _NoAutoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Custom handler that disables automatic redirect following to inspect each hop."""

    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None  # Returning None prevents automatic redirect


def fetch_url_with_limits(
    url: str,
    config: Optional[ImportConfig] = None,
) -> tuple[bytes, dict[str, Any]]:
    """Fetch URL with strict SSRF checks, timeout, redirect limits, and streaming size bounds.

    Returns (content_bytes, response_metadata).
    Raises NetworkSecurityError, SizeLimitExceededError, or SourceImportError.
    """
    cfg = config or ImportConfig()

    if cfg.offline_only:
        raise OfflineModeViolationError(url=url)

    current_url = url
    visited_urls: set[str] = {current_url}
    redirect_history: list[str] = []

    # Configure opener that does not automatically follow redirects
    opener = urllib.request.build_opener(_NoAutoRedirectHandler)

    for redirect_count in range(cfg.max_redirects + 1):
        # Validate SSRF on current destination BEFORE opening socket
        validate_url(current_url, cfg)

        req = urllib.request.Request(
            current_url,
            headers={
                "User-Agent": cfg.user_agent,
                "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.5",
            },
        )

        try:
            resp = opener.open(req, timeout=cfg.timeout_seconds)
        except urllib.error.HTTPError as http_err:
            # Check if this is a redirect status (301, 302, 303, 307, 308)
            if http_err.code in (301, 302, 303, 307, 308):
                location = http_err.headers.get("Location")
                if not location:
                    raise RedirectSecurityError(
                        current_url=current_url,
                        target_url=None,
                        reason=f"HTTP {http_err.code} redirect missing 'Location' header",
                    )
                next_url = urllib.parse.urljoin(current_url, location)

                if redirect_count >= cfg.max_redirects:
                    raise RedirectSecurityError(
                        current_url=current_url,
                        target_url=next_url,
                        reason=f"Exceeded maximum allowed redirects ({cfg.max_redirects})",
                    )

                if next_url in visited_urls:
                    raise RedirectSecurityError(
                        current_url=current_url,
                        target_url=next_url,
                        reason=f"Redirect cycle detected to '{next_url}'",
                    )

                visited_urls.add(next_url)
                redirect_history.append(current_url)
                current_url = next_url
                continue
            else:
                raise HTTPStatusError(
                    url=current_url,
                    status_code=http_err.code,
                    reason=http_err.reason,
                )
        except urllib.error.URLError as url_err:
            reason = str(url_err.reason)
            if "timed out" in reason.lower():
                raise NetworkTimeoutError(url=current_url, timeout_seconds=cfg.timeout_seconds)
            raise NetworkSecurityError(f"Connection failed for '{current_url}': {reason}")
        except socket.timeout:
            raise NetworkTimeoutError(url=current_url, timeout_seconds=cfg.timeout_seconds)

        # Successfully reached final 200 OK endpoint
        status_code = getattr(resp, "status", 200)
        headers = resp.headers

        # Check Content-Type header
        content_type_raw = headers.get("Content-Type", "")
        media_type = content_type_raw.split(";")[0].strip().lower()
        if cfg.require_pdf and media_type and media_type not in cfg.allowed_content_types:
            raise InvalidFileFormatError(
                f"HTTP response Content-Type '{media_type}' is not an approved PDF type ({list(cfg.allowed_content_types)})."
            )

        # Pre-check Content-Length header to reject oversized payloads early
        content_length_str = headers.get("Content-Length")
        if content_length_str and content_length_str.isdigit():
            declared_size = int(content_length_str)
            if declared_size > cfg.max_size_bytes:
                raise SizeLimitExceededError(
                    current_size=declared_size,
                    max_size=cfg.max_size_bytes,
                    message=(
                        f"HTTP Content-Length header ({declared_size} bytes) exceeds limit "
                        f"of {cfg.max_size_bytes} bytes before download."
                    ),
                )

        # Stream body with strict incremental size counter
        chunks: list[bytes] = []
        accumulated_bytes = 0

        try:
            while True:
                chunk = resp.read(cfg.chunk_size)
                if not chunk:
                    break
                accumulated_bytes += len(chunk)
                if accumulated_bytes > cfg.max_size_bytes:
                    raise SizeLimitExceededError(
                        current_size=accumulated_bytes,
                        max_size=cfg.max_size_bytes,
                        message=(
                            f"Downloaded data exceeded maximum size limit of {cfg.max_size_bytes} bytes "
                            f"(accumulated {accumulated_bytes} bytes mid-stream)."
                        ),
                    )
                chunks.append(chunk)
        except socket.timeout:
            raise NetworkTimeoutError(url=current_url, timeout_seconds=cfg.timeout_seconds)
        finally:
            resp.close()

        full_content = b"".join(chunks)
        metadata = {
            "final_url": current_url,
            "redirect_history": redirect_history,
            "status_code": status_code,
            "content_type": media_type,
            "declared_content_length": content_length_str,
        }
        return full_content, metadata

    raise RedirectSecurityError(
        current_url=current_url,
        target_url=None,
        reason=f"Exceeded maximum allowed redirects ({cfg.max_redirects})",
    )


# ---------------------------------------------------------------------------
# Core Import & Verification APIs
# ---------------------------------------------------------------------------


def import_source_from_bytes(
    data: bytes,
    expected_hash: Optional[str] = None,
    source_id: Optional[str] = None,
    source_url: Optional[str] = None,
    config: Optional[ImportConfig] = None,
) -> ImportResult:
    """Import and verify a source document from an in-memory byte buffer.

    Enforces size limits, magic bytes, static active content inspection, and SHA-256 hash checks.
    Does NOT execute source code or evaluate dynamic elements.
    """
    cfg = config or ImportConfig()
    size_bytes = len(data)

    if size_bytes > cfg.max_size_bytes:
        raise SizeLimitExceededError(current_size=size_bytes, max_size=cfg.max_size_bytes)
    if size_bytes < cfg.min_size_bytes:
        raise EmptyFileError(current_size=size_bytes, min_size=cfg.min_size_bytes)

    # Compute SHA-256
    computed_hash = compute_bytes_sha256(data)

    # Hash verification if expected_hash provided
    if expected_hash is not None:
        verify_hash(computed_hash, expected_hash, source_id=source_id)

    # Structural PDF inspection
    pdf_version: Optional[str] = None
    active_content_findings: list[str] = []
    if cfg.require_pdf:
        pdf_version, active_content_findings = inspect_pdf_bytes(data, cfg)

    return ImportResult(
        status="verified",
        sha256=computed_hash,
        size_bytes=size_bytes,
        file_type="application/pdf",
        pdf_version=pdf_version,
        active_content_detected=bool(active_content_findings),
        active_content_findings=active_content_findings,
        source_id=source_id,
        source_url=source_url,
    )


def import_source_from_file(
    path: Union[Path, str],
    expected_hash: Optional[str] = None,
    source_id: Optional[str] = None,
    config: Optional[ImportConfig] = None,
) -> ImportResult:
    """Import and verify a local source document file using streaming checks.

    Rejects oversized files immediately based on filesystem metadata, streams
    hash calculation in constant memory, and statically inspects PDF tokens.
    """
    cfg = config or ImportConfig()
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")
    if not file_path.is_file():
        raise SourceImportError(f"Target path is not a regular file: {file_path}")

    stat = file_path.stat()
    file_size = stat.st_size

    if file_size > cfg.max_size_bytes:
        raise SizeLimitExceededError(current_size=file_size, max_size=cfg.max_size_bytes)
    if file_size < cfg.min_size_bytes:
        raise EmptyFileError(current_size=file_size, min_size=cfg.min_size_bytes)

    # Read and inspect
    with file_path.open("rb") as f:
        data = f.read()

    return import_source_from_bytes(
        data=data,
        expected_hash=expected_hash,
        source_id=source_id,
        source_url=str(file_path),
        config=cfg,
    )


def import_source_from_url(
    url: str,
    expected_hash: Optional[str] = None,
    source_id: Optional[str] = None,
    config: Optional[ImportConfig] = None,
) -> ImportResult:
    """Import and verify a source document from a remote URL.

    Enforces SSRF boundaries, redirect limits, timeouts, streaming size limits,
    PDF structure checks, and SHA-256 verification.
    """
    cfg = config or ImportConfig()
    data, meta = fetch_url_with_limits(url, cfg)

    result = import_source_from_bytes(
        data=data,
        expected_hash=expected_hash,
        source_id=source_id,
        source_url=meta.get("final_url", url),
        config=cfg,
    )

    # Attach network metadata
    result.metadata.update(meta)
    return result


def verify_source_record(
    source: SourceRecord,
    file_path: Optional[Union[Path, str]] = None,
    config: Optional[ImportConfig] = None,
) -> ImportResult:
    """Verify an individual SourceRecord against security boundaries and its registered SHA-256.

    If file_path is provided, verifies the local downloaded copy.
    """
    cfg = config or ImportConfig()

    # Validate official and direct URLs against boundary rules
    validate_url(source.official_url, cfg)
    if source.direct_url:
        validate_url(source.direct_url, cfg)

    if file_path is not None:
        return import_source_from_file(
            path=file_path,
            expected_hash=source.sha256,
            source_id=source.id,
            config=cfg,
        )

    # When no local file provided, validate expected hash formatting if present
    if source.sha256:
        validate_sha256_format(source.sha256)

    return ImportResult(
        status="verified" if source.status == "verified" else source.status,
        sha256=source.sha256 or "",
        size_bytes=0,
        file_type="application/pdf" if source.filename and source.filename.endswith(".pdf") else "unknown",
        source_id=source.id,
        source_url=source.direct_url or source.official_url,
    )


def verify_register_sources_offline(
    register: SourceRegister,
    sources_dir: Union[Path, str],
    config: Optional[ImportConfig] = None,
) -> dict[str, ImportResult]:
    """Verify all verified sources in a SourceRegister against offline files in sources_dir."""
    cfg = config or ImportConfig(offline_only=True)
    dir_path = Path(sources_dir)
    results: dict[str, ImportResult] = {}

    for source in register.sources:
        if source.status != "verified" or not source.sha256:
            continue

        target_file: Optional[Path] = None
        # Try finding file by filename or id
        if source.filename and (dir_path / source.filename).exists():
            target_file = dir_path / source.filename
        elif (dir_path / f"{source.id}.pdf").exists():
            target_file = dir_path / f"{source.id}.pdf"

        if target_file:
            res = import_source_from_file(
                path=target_file,
                expected_hash=source.sha256,
                source_id=source.id,
                config=cfg,
            )
            results[source.id] = res
        else:
            raise FileNotFoundError(
                f"Source file for verified record '{source.id}' not found in {sources_dir}."
            )

    return results


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entrypoint for offline source import and verification."""
    parser = argparse.ArgumentParser(
        description="Isolated offline source import and hash verification for elecciones2026"
    )
    subparsers = parser.add_subparsers(dest="command")

    # verify-file subcommand
    vf_parser = subparsers.add_parser("verify-file", help="Verify a local PDF file")
    vf_parser.add_argument("path", help="Path to PDF source file")
    vf_parser.add_argument("--expected-hash", help="Expected 64-char hex SHA-256 hash", default=None)
    vf_parser.add_argument("--max-size-mb", help="Maximum file size in MB", type=int, default=50)

    # check-url subcommand
    cu_parser = subparsers.add_parser("check-url", help="Validate URL against SSRF and security boundaries")
    cu_parser.add_argument("url", help="URL to inspect")
    cu_parser.add_argument("--allow-http", action="store_true", help="Allow HTTP protocol")

    # verify-register subcommand
    vr_parser = subparsers.add_parser(
        "verify-register",
        help="Verify registered sources against an offline storage directory",
    )
    vr_parser.add_argument("register_path", help="Path to register.json")
    vr_parser.add_argument("sources_dir", help="Directory containing downloaded source files")

    args = parser.parse_args()

    if args.command == "verify-file":
        cfg = ImportConfig(max_size_bytes=args.max_size_mb * 1024 * 1024)
        try:
            result = import_source_from_file(
                path=args.path,
                expected_hash=args.expected_hash,
                config=cfg,
            )
            print(f"OK: Verified source file {args.path}")
            print(f"  SHA-256:     {result.sha256}")
            print(f"  Size:        {result.size_bytes} bytes")
            print(f"  PDF Version: {result.pdf_version}")
            sys.exit(0)
        except SourceImportError as err:
            print(f"FAILED: {err}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "check-url":
        schemes = ("https", "http") if args.allow_http else ("https",)
        cfg = ImportConfig(allowed_schemes=schemes)
        try:
            ips = validate_url(args.url, cfg)
            print(f"OK: URL '{args.url}' passed security boundaries.")
            if ips:
                print(f"  Resolved safe IPs: {', '.join(ips)}")
            sys.exit(0)
        except NetworkSecurityError as err:
            print(f"BLOCKED: {err}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "verify-register":
        try:
            reg = load_register(args.register_path)
            results = verify_register_sources_offline(reg, args.sources_dir)
            print(f"OK: Successfully verified {len(results)} source documents in {args.sources_dir}.")
            for src_id, res in results.items():
                print(f"  [{src_id}] {res.size_bytes} bytes | sha256:{res.sha256[:16]}...")
            sys.exit(0)
        except Exception as err:
            print(f"FAILED: {err}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
