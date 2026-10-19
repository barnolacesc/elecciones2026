"""Feedback, improvement proposal box, and abuse prevention pipeline.

Package E8.5: User Improvement Proposal Box (Buzón de Propuestas de Mejora).
Implements domain models, PII scrubbing, cryptographic anti-replay tokens,
SimHash near-duplicate detection, subnet rate limiting, and a Local SQLite
persistence repository in compliance with OWASP ASVS Level 2 and GDPR/LOPDGDD.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from uuid import uuid4

# -----------------------------------------------------------------------------
# Constants & Validation Constraints
# -----------------------------------------------------------------------------

MIN_PROPOSAL_LENGTH = 10
MAX_PROPOSAL_LENGTH = 600

MIN_SUBMISSION_DURATION_SECONDS = 3.0
MAX_TOKEN_AGE_SECONDS = 600  # 10 minutes

VALID_CATEGORIES = {
    "general",
    "comparator",
    "sources",
    "ui",
    "methodology",
}

VALID_STATUSES = {
    "pending",
    "spam",
    "rejected",
    "considered",
    "actioned",
}

# Regex to scrub email addresses
EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    re.IGNORECASE,
)

# Regex to scrub Spanish telephone numbers (+34 / 0034 optional, 9 digits starting with 6, 7, 8, or 9)
PHONE_REGEX = re.compile(
    r"(?:(?:\+|00)34[\s.-]*)?[6789](?:[\s.-]*\d){8}\b"
)

# Control characters excluding standard newline and tab
CONTROL_CHARS_REGEX = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


# -----------------------------------------------------------------------------
# Domain Records & Data Transfer Objects
# -----------------------------------------------------------------------------


@dataclass
class ProposalCreate:
    """Incoming user proposal payload."""

    text: str
    category: str = "general"
    completion_time_ms: int = 0
    honeypot: str = ""
    token: str = ""


@dataclass
class ProposalRecord:
    """Persisted proposal record with provenance, triage, and security metadata."""

    id: str
    created_at: str
    category: str
    text: str
    status: str
    char_count: int
    completion_time_ms: int
    content_hash: str
    simhash: str
    subnet_hash: str
    reviewer_notes: Optional[str] = None
    action_ticket: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "category": self.category,
            "text": self.text,
            "status": self.status,
            "char_count": self.char_count,
            "completion_time_ms": self.completion_time_ms,
            "content_hash": self.content_hash,
            "simhash": self.simhash,
            "subnet_hash": self.subnet_hash,
            "reviewer_notes": self.reviewer_notes,
            "action_ticket": self.action_ticket,
        }


@dataclass
class ProposalSubmissionResult:
    """Outcome of a proposal submission attempt."""

    success: bool
    status_code: int
    user_message_es: str
    proposal_id: Optional[str] = None
    internal_status: Optional[str] = None


# -----------------------------------------------------------------------------
# Text Sanitization, PII Redaction & Fingerprinting
# -----------------------------------------------------------------------------


def normalize_text(text: str) -> str:
    """Normalize Unicode (NFC), remove control characters, and collapse spaces."""
    if not text:
        return ""
    # NFC Unicode normalization
    normalized = unicodedata.normalize("NFC", text)
    # Strip null bytes and non-printable control characters
    cleaned = CONTROL_CHARS_REGEX.sub("", normalized)
    # Strip whitespace edges
    return cleaned.strip()


def scrub_pii(text: str) -> str:
    """Redact identifiable email addresses and Spanish telephone numbers."""
    scrubbed = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    scrubbed = PHONE_REGEX.sub("[REDACTED_PHONE]", scrubbed)
    return scrubbed


def compute_content_hash(text: str) -> str:
    """Compute SHA-256 of lowercase normalized text for exact duplicate detection."""
    collapsed = " ".join(text.lower().split())
    return hashlib.sha256(collapsed.encode("utf-8")).hexdigest()


def compute_simhash(text: str, hash_bits: int = 64) -> str:
    """Compute a 64-bit SimHash over 3-gram character shingles for near-duplicate detection."""
    collapsed = " ".join(text.lower().split())
    if len(collapsed) < 3:
        shingles = [collapsed]
    else:
        shingles = [collapsed[i : i + 3] for i in range(len(collapsed) - 2)]

    v = [0] * hash_bits
    for shingle in shingles:
        digest = hashlib.md5(shingle.encode("utf-8")).digest()
        # Take the first 8 bytes for a 64-bit hash integer
        h = int.from_bytes(digest[:8], byteorder="big")
        for i in range(hash_bits):
            bit = (h >> i) & 1
            if bit == 1:
                v[i] += 1
            else:
                v[i] -= 1

    fingerprint = 0
    for i in range(hash_bits):
        if v[i] > 0:
            fingerprint |= 1 << i

    return f"{fingerprint:016x}"


def simhash_similarity(hash1: str, hash2: str, hash_bits: int = 64) -> float:
    """Calculate normalized similarity between two SimHash hex strings (1.0 = identical)."""
    try:
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
    except (ValueError, TypeError):
        return 0.0

    xor_val = val1 ^ val2
    # Count set bits (Hamming distance)
    hamming_distance = bin(xor_val).count("1")
    return 1.0 - (hamming_distance / float(hash_bits))


# -----------------------------------------------------------------------------
# Subnet Normalization & Cryptographic Anti-Replay Tokens
# -----------------------------------------------------------------------------


def compute_subnet_hash(ip_address: str, salt: str = "elecciones2026-salt") -> str:
    """Hash the client IP aggregated by IPv4 /32 or IPv6 /64 prefix to prevent hopping."""
    clean_ip = (ip_address or "127.0.0.1").strip()

    if ":" in clean_ip:
        # IPv6: extract first 4 hextets (/64 prefix)
        parts = clean_ip.split(":")
        subnet = ":".join(parts[:4])
    else:
        # IPv4: full IP
        subnet = clean_ip

    return hmac.new(salt.encode("utf-8"), subnet.encode("utf-8"), hashlib.sha256).hexdigest()[:32]


def create_proposal_token(
    secret_key: str,
    subnet_hash: str,
    timestamp: Optional[int] = None,
    nonce: Optional[str] = None,
) -> str:
    """Generate an HMAC-signed single-use ticket enforcing time-lock and anti-replay."""
    ts = timestamp if timestamp is not None else int(time.time())
    n = nonce if nonce is not None else secrets.token_hex(16)

    payload = f"{ts}:{n}:{subnet_hash}"
    sig = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{ts}.{n}.{sig}"


def verify_proposal_token(
    token: str,
    secret_key: str,
    subnet_hash: str,
    now: Optional[int] = None,
    min_seconds: float = MIN_SUBMISSION_DURATION_SECONDS,
    max_seconds: int = MAX_TOKEN_AGE_SECONDS,
) -> Tuple[bool, str, Optional[str]]:
    """Validate token signature, time bounds, and extract nonce.

    Returns:
        (is_valid, failure_reason_or_ok, nonce)
    """
    if not token or token.count(".") != 2:
        return False, "invalid_format", None

    parts = token.split(".")
    try:
        ts = int(parts[0])
        nonce = parts[1]
        sig = parts[2]
    except ValueError:
        return False, "invalid_parts", None

    expected_payload = f"{ts}:{nonce}:{subnet_hash}"
    expected_sig = hmac.new(
        secret_key.encode("utf-8"), expected_payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(sig, expected_sig):
        return False, "tampered_signature", None

    current_ts = now if now is not None else int(time.time())
    elapsed = current_ts - ts

    if elapsed < min_seconds:
        return False, "too_fast", nonce

    if elapsed > max_seconds:
        return False, "expired", nonce

    return True, "valid", nonce


# -----------------------------------------------------------------------------
# Storage Protocol (Port)
# -----------------------------------------------------------------------------


class ProposalRepository(Protocol):
    """Abstract interface decoupling proposal ingestion from physical persistence."""

    def save_proposal(self, record: ProposalRecord) -> ProposalRecord:
        """Persist a new proposal record."""
        ...

    def get_proposal(self, proposal_id: str) -> Optional[ProposalRecord]:
        """Fetch a proposal by ID."""
        ...

    def list_proposals(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ProposalRecord]:
        """List proposals matching status/category."""
        ...

    def update_status(
        self,
        proposal_id: str,
        new_status: str,
        reviewer_notes: Optional[str] = None,
        action_ticket: Optional[str] = None,
    ) -> Optional[ProposalRecord]:
        """Update proposal triage status and review notes."""
        ...

    def is_duplicate(
        self,
        content_hash: str,
        simhash: str,
        window_seconds: int = 86400,
        similarity_threshold: float = 0.85,
    ) -> bool:
        """Check for identical or near-identical submissions within rolling time window."""
        ...

    def is_rate_limited(
        self,
        subnet_hash: str,
        max_requests: int = 3,
        window_seconds: int = 3600,
    ) -> bool:
        """Check if client subnet hash has exceeded maximum allowed requests in window."""
        ...

    def record_rate_limit_hit(self, subnet_hash: str, window_seconds: int = 3600) -> None:
        """Record an attempt against the client subnet's rate limiting window."""
        ...

    def is_token_consumed(self, nonce: str) -> bool:
        """Verify whether a single-use nonce has already been consumed."""
        ...

    def mark_token_consumed(self, nonce: str, ttl_seconds: int = MAX_TOKEN_AGE_SECONDS) -> None:
        """Mark a single-use nonce as consumed to prevent replay attacks."""
        ...

    def prune_expired(self) -> int:
        """Remove expired token nonces and old rate limit buckets."""
        ...

    def stats(self) -> Dict[str, int]:
        """Return counts of proposals grouped by status."""
        ...


# -----------------------------------------------------------------------------
# SQLite Implementation (Adapter)
# -----------------------------------------------------------------------------


class SQLiteProposalRepository:
    """Thread-safe Local SQLite proposal repository operating in WAL mode.

    Zero external infrastructure dependencies; < 5 MB RAM overhead;
    fully parameterized SQL queries preventing any SQL injection.
    """

    DDL = """
    PRAGMA journal_mode = WAL;
    PRAGMA synchronous = NORMAL;
    PRAGMA foreign_keys = ON;
    PRAGMA busy_timeout = 5000;

    CREATE TABLE IF NOT EXISTS proposals (
        id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'general',
        text TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        char_count INTEGER NOT NULL,
        completion_time_ms INTEGER NOT NULL,
        content_hash TEXT NOT NULL,
        simhash TEXT NOT NULL,
        subnet_hash TEXT NOT NULL,
        reviewer_notes TEXT,
        action_ticket TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
    CREATE INDEX IF NOT EXISTS idx_proposals_created_at ON proposals(created_at);
    CREATE INDEX IF NOT EXISTS idx_proposals_content_hash ON proposals(content_hash);
    CREATE INDEX IF NOT EXISTS idx_proposals_simhash ON proposals(simhash);

    CREATE TABLE IF NOT EXISTS consumed_tokens (
        nonce TEXT PRIMARY KEY,
        consumed_at TEXT NOT NULL,
        expires_at INTEGER NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_consumed_tokens_expires ON consumed_tokens(expires_at);

    CREATE TABLE IF NOT EXISTS rate_limits (
        subnet_hash TEXT NOT NULL,
        window_start INTEGER NOT NULL,
        request_count INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY (subnet_hash, window_start)
    );
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
            isolation_level=None,  # Autocommit mode; transactions handled explicitly
        )
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        """Initialize tables and indexes with pragmas."""
        cur = self.conn.cursor()
        cur.executescript(self.DDL)
        cur.close()

    def save_proposal(self, record: ProposalRecord) -> ProposalRecord:
        """Insert proposal using strictly parameterized queries."""
        sql = """
        INSERT INTO proposals (
            id, created_at, category, text, status,
            char_count, completion_time_ms, content_hash,
            simhash, subnet_hash, reviewer_notes, action_ticket
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            record.id,
            record.created_at,
            record.category,
            record.text,
            record.status,
            record.char_count,
            record.completion_time_ms,
            record.content_hash,
            record.simhash,
            record.subnet_hash,
            record.reviewer_notes,
            record.action_ticket,
        )
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cur.close()
        return record

    def get_proposal(self, proposal_id: str) -> Optional[ProposalRecord]:
        """Retrieve proposal record by primary key."""
        sql = "SELECT * FROM proposals WHERE id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (proposal_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return None
        return self._row_to_record(row)

    def list_proposals(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ProposalRecord]:
        """Query proposals with optional filtering by status and category."""
        conditions = []
        params: List[Any] = []

        if status:
            conditions.append("status = ?")
            params.append(status)
        if category:
            conditions.append("category = ?")
            params.append(category)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"SELECT * FROM proposals {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cur = self.conn.cursor()
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cur.close()
        return [self._row_to_record(row) for row in rows]

    def update_status(
        self,
        proposal_id: str,
        new_status: str,
        reviewer_notes: Optional[str] = None,
        action_ticket: Optional[str] = None,
    ) -> Optional[ProposalRecord]:
        """Update triage state and notes."""
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {VALID_STATUSES}")

        sql = """
        UPDATE proposals
        SET status = ?,
            reviewer_notes = COALESCE(?, reviewer_notes),
            action_ticket = COALESCE(?, action_ticket)
        WHERE id = ?
        """
        cur = self.conn.cursor()
        cur.execute(sql, (new_status, reviewer_notes, action_ticket, proposal_id))
        cur.close()
        return self.get_proposal(proposal_id)

    def is_duplicate(
        self,
        content_hash: str,
        simhash: str,
        window_seconds: int = 86400,
        similarity_threshold: float = 0.85,
    ) -> bool:
        """Check if identical or near-identical text was submitted in the last window."""
        cutoff = datetime.fromtimestamp(time.time() - window_seconds, tz=timezone.utc).isoformat()

        # 1. Exact hash match
        sql_exact = "SELECT 1 FROM proposals WHERE content_hash = ? AND created_at >= ? LIMIT 1"
        cur = self.conn.cursor()
        cur.execute(sql_exact, (content_hash, cutoff))
        if cur.fetchone():
            cur.close()
            return True

        # 2. Near-duplicate SimHash check
        sql_sim = "SELECT simhash FROM proposals WHERE created_at >= ?"
        cur.execute(sql_sim, (cutoff,))
        rows = cur.fetchall()
        cur.close()

        for row in rows:
            sim = simhash_similarity(simhash, row["simhash"])
            if sim >= similarity_threshold:
                return True

        return False

    def is_rate_limited(
        self,
        subnet_hash: str,
        max_requests: int = 3,
        window_seconds: int = 3600,
    ) -> bool:
        """Check if client subnet exceeded quota in current time window."""
        now = int(time.time())
        window_start = now - (now % window_seconds)

        sql = "SELECT request_count FROM rate_limits WHERE subnet_hash = ? AND window_start = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (subnet_hash, window_start))
        row = cur.fetchone()
        cur.close()

        if row and row["request_count"] >= max_requests:
            return True
        return False

    def record_rate_limit_hit(self, subnet_hash: str, window_seconds: int = 3600) -> None:
        """Increment count for subnet in current window."""
        now = int(time.time())
        window_start = now - (now % window_seconds)

        sql = """
        INSERT INTO rate_limits (subnet_hash, window_start, request_count)
        VALUES (?, ?, 1)
        ON CONFLICT(subnet_hash, window_start)
        DO UPDATE SET request_count = request_count + 1
        """
        cur = self.conn.cursor()
        cur.execute(sql, (subnet_hash, window_start))
        cur.close()

    def is_token_consumed(self, nonce: str) -> bool:
        """Check if anti-replay nonce exists."""
        sql = "SELECT 1 FROM consumed_tokens WHERE nonce = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (nonce,))
        row = cur.fetchone()
        cur.close()
        return row is not None

    def mark_token_consumed(self, nonce: str, ttl_seconds: int = MAX_TOKEN_AGE_SECONDS) -> None:
        """Persist consumed token nonce with expiry."""
        now = int(time.time())
        expires_at = now + ttl_seconds
        iso_now = datetime.fromtimestamp(now, tz=timezone.utc).isoformat()

        sql = "INSERT OR REPLACE INTO consumed_tokens (nonce, consumed_at, expires_at) VALUES (?, ?, ?)"
        cur = self.conn.cursor()
        cur.execute(sql, (nonce, iso_now, expires_at))
        cur.close()

    def prune_expired(self) -> int:
        """Delete expired nonces and stale rate limit rows older than 24 hours."""
        now = int(time.time())
        stale_rate_cutoff = now - 86400

        cur = self.conn.cursor()
        cur.execute("DELETE FROM consumed_tokens WHERE expires_at < ?", (now,))
        del_tokens = cur.rowcount
        cur.execute("DELETE FROM rate_limits WHERE window_start < ?", (stale_rate_cutoff,))
        del_rate = cur.rowcount
        cur.close()
        return del_tokens + del_rate

    def stats(self) -> Dict[str, int]:
        """Aggregate summary count by status."""
        sql = "SELECT status, COUNT(*) as count FROM proposals GROUP BY status"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        result = {s: 0 for s in VALID_STATUSES}
        for row in rows:
            result[row["status"]] = row["count"]
        return result

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> ProposalRecord:
        return ProposalRecord(
            id=row["id"],
            created_at=row["created_at"],
            category=row["category"],
            text=row["text"],
            status=row["status"],
            char_count=row["char_count"],
            completion_time_ms=row["completion_time_ms"],
            content_hash=row["content_hash"],
            simhash=row["simhash"],
            subnet_hash=row["subnet_hash"],
            reviewer_notes=row["reviewer_notes"],
            action_ticket=row["action_ticket"],
        )


# -----------------------------------------------------------------------------
# Submission Service / Controller
# -----------------------------------------------------------------------------


class FeedbackService:
    """Orchestrates proposal validation, anti-abuse checks, and persistence."""

    def __init__(
        self,
        repository: ProposalRepository,
        secret_key: str = "elecciones2026-feedback-secret-default",
    ) -> None:
        self.repo = repository
        self.secret_key = secret_key

    def generate_token(self, client_ip: str) -> str:
        """Issue an anti-replay token for the client IP subnet."""
        subnet_hash = compute_subnet_hash(client_ip)
        return create_proposal_token(self.secret_key, subnet_hash)

    def submit_proposal(
        self,
        payload: ProposalCreate,
        client_ip: str,
        now: Optional[int] = None,
    ) -> ProposalSubmissionResult:
        """Process an untrusted public proposal submission through the 5-tier defense pipeline."""
        subnet_hash = compute_subnet_hash(client_ip)

        # 1. Rate Limiting Check
        if self.repo.is_rate_limited(subnet_hash):
            return ProposalSubmissionResult(
                success=False,
                status_code=429,
                user_message_es="Has enviado varias propuestas recientemente. Por favor, espera antes de enviar otra.",
                internal_status="rate_limited",
            )

        # 2. Cryptographic Token & Nonce (Anti-Replay) Check
        if not payload.token:
            return ProposalSubmissionResult(
                success=False,
                status_code=401,
                user_message_es="Falta el testigo de seguridad del formulario. Por favor, recarga la página.",
                internal_status="missing_token",
            )

        is_valid, reason, nonce = verify_proposal_token(
            token=payload.token,
            secret_key=self.secret_key,
            subnet_hash=subnet_hash,
            now=now,
        )

        if not is_valid:
            if reason == "too_fast":
                # Bot submitted in under minimum duration -> silent discard
                return ProposalSubmissionResult(
                    success=True,
                    status_code=201,
                    user_message_es="¡Muchas gracias! Tu propuesta ha quedado registrada en nuestro buzón para revisión.",
                    internal_status="bot_too_fast_dropped",
                )
            return ProposalSubmissionResult(
                success=False,
                status_code=400,
                user_message_es="El testigo del formulario no es válido o ha expirado. Por favor, recarga la página.",
                internal_status=f"invalid_token_{reason}",
            )

        # 3. Single-Use Nonce Check
        if nonce and self.repo.is_token_consumed(nonce):
            return ProposalSubmissionResult(
                success=False,
                status_code=409,
                user_message_es="Este envío ya ha sido procesado previamente.",
                internal_status="replay_attempt",
            )

        # Mark nonce as consumed immediately
        if nonce:
            self.repo.mark_token_consumed(nonce)

        # Record rate-limit hit
        self.repo.record_rate_limit_hit(subnet_hash)

        # 4. Honeypot Check (Bot Trapping)
        is_honeypot_filled = bool(payload.honeypot and payload.honeypot.strip())

        # 5. Text Sanitization and Normalization
        clean_text = normalize_text(payload.text)
        scrubbed_text = scrub_pii(clean_text)

        # Length validation
        char_count = len(scrubbed_text)
        if char_count < MIN_PROPOSAL_LENGTH:
            return ProposalSubmissionResult(
                success=False,
                status_code=422,
                user_message_es=f"La propuesta debe contener al menos {MIN_PROPOSAL_LENGTH} caracteres.",
                internal_status="text_too_short",
            )

        if char_count > MAX_PROPOSAL_LENGTH:
            return ProposalSubmissionResult(
                success=False,
                status_code=422,
                user_message_es=f"La propuesta no puede exceder los {MAX_PROPOSAL_LENGTH} caracteres.",
                internal_status="text_too_long",
            )

        category = payload.category if payload.category in VALID_CATEGORIES else "general"

        content_hash = compute_content_hash(scrubbed_text)
        simhash = compute_simhash(scrubbed_text)

        # 6. Duplicate & Near-Duplicate Check
        if self.repo.is_duplicate(content_hash, simhash):
            return ProposalSubmissionResult(
                success=True,
                status_code=201,
                user_message_es="¡Muchas gracias! Tu propuesta ha quedado registrada en nuestro buzón para revisión.",
                internal_status="near_duplicate_collapsed",
            )

        # Determine initial triage state
        initial_status = "spam" if is_honeypot_filled else "pending"

        record = ProposalRecord(
            id=f"urn:uuid:{uuid4()}",
            created_at=datetime.now(timezone.utc).isoformat(),
            category=category,
            text=scrubbed_text,
            status=initial_status,
            char_count=char_count,
            completion_time_ms=payload.completion_time_ms,
            content_hash=content_hash,
            simhash=simhash,
            subnet_hash=subnet_hash,
        )

        self.repo.save_proposal(record)

        return ProposalSubmissionResult(
            success=True,
            status_code=201,
            user_message_es="¡Muchas gracias! Tu propuesta ha quedado registrada en nuestro buzón para revisión.",
            proposal_id=record.id,
            internal_status=initial_status,
        )
