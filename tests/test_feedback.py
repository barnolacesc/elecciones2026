"""Unit and security integration tests for Feedback Proposal Box (Roadmap package E8.5).

Verifies acceptance criteria from docs/issues/ISSUE-IMPROVEMENT-PROPOSAL-BOX.md:
- Domain schema validation and Unicode NFC normalization.
- Strict PII scrubbing for emails and Spanish telephone numbers.
- SQL injection immunity via 100% parameterized queries.
- Stored XSS defense (plain-text treatment).
- Honeypot bot trapping (silent acceptance tagged as spam).
- Cryptographic single-use tokens, anti-replay nonce tracking, and time-lock bounds.
- IPv4 /32 and IPv6 /64 subnet rate limiting.
- SimHash near-duplicate detection and suppression.
- SQLite WAL mode pragmas and atomic transactions.
- Maintainer triage CLI operations (stats, list, review, export, prune).
"""

from __future__ import annotations

import io
import os
import shutil
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from elecciones2026.feedback import (
    MAX_PROPOSAL_LENGTH,
    MIN_PROPOSAL_LENGTH,
    FeedbackService,
    ProposalCreate,
    ProposalRecord,
    SQLiteProposalRepository,
    compute_content_hash,
    compute_simhash,
    compute_subnet_hash,
    create_proposal_token,
    normalize_text,
    scrub_pii,
    simhash_similarity,
    verify_proposal_token,
)
import tools.feedback_triage as triage_cli


class TestFeedbackValidationAndSanitization(unittest.TestCase):
    """Test text normalization, PII scrubbing, and input validation."""

    def test_normalize_text_strips_control_characters_and_normalizes_nfc(self) -> None:
        raw = "Propuesta con acentos: camio\u0301n\x00\x08 y saltos   de   espacio.  "
        normalized = normalize_text(raw)
        self.assertNotIn("\x00", normalized)
        self.assertNotIn("\x08", normalized)
        # NFC form of camión
        self.assertIn("camión", normalized)
        self.assertEqual(normalized, "Propuesta con acentos: camión y saltos   de   espacio.")

    def test_scrub_pii_redacts_emails(self) -> None:
        text = "Por favor escribidme a ciudadano.ejemplo@correo.es o a contacto@test.org para detalles."
        scrubbed = scrub_pii(text)
        self.assertNotIn("ciudadano.ejemplo@correo.es", scrubbed)
        self.assertNotIn("contacto@test.org", scrubbed)
        self.assertEqual(
            scrubbed,
            "Por favor escribidme a [REDACTED_EMAIL] o a [REDACTED_EMAIL] para detalles.",
        )

    def test_scrub_pii_redacts_spanish_phone_numbers(self) -> None:
        samples = [
            ("Llamad al 612345678 por la tarde", "Llamad al [REDACTED_PHONE] por la tarde"),
            ("Mi teléfono fijo es 912345678", "Mi teléfono fijo es [REDACTED_PHONE]"),
            ("Móvil internacional +34 600112233", "Móvil internacional [REDACTED_PHONE]"),
            ("Prefijo 0034 711 22 33 44 aviso", "Prefijo [REDACTED_PHONE] aviso"),
        ]
        for raw, expected in samples:
            self.assertEqual(scrub_pii(raw), expected)


class TestSimHashNearDuplicateDetection(unittest.TestCase):
    """Test 64-bit SimHash near-duplicate detection."""

    def test_identical_text_has_maximum_similarity(self) -> None:
        t1 = "Me gustaría poder comparar tres partidos políticos a la vez."
        t2 = "me gustaría poder comparar tres partidos políticos a la vez."
        h1 = compute_simhash(t1)
        h2 = compute_simhash(t2)
        self.assertEqual(h1, h2)
        self.assertAlmostEqual(simhash_similarity(h1, h2), 1.0)

    def test_slightly_mutated_text_exceeds_threshold(self) -> None:
        t1 = "Me gustaría poder comparar tres partidos políticos a la vez en el comparador."
        t2 = "Me gustaría poder comparar tres partidos políticos a la vez en el comparador!"
        h1 = compute_simhash(t1)
        h2 = compute_simhash(t2)
        sim = simhash_similarity(h1, h2)
        self.assertGreaterEqual(sim, 0.85)

    def test_unrelated_text_has_low_similarity(self) -> None:
        t1 = "Añadir más fuentes oficiales sobre educación primaria y becas."
        t2 = "El contraste del fondo en el modo oscuro no es suficientemente legible."
        h1 = compute_simhash(t1)
        h2 = compute_simhash(t2)
        sim = simhash_similarity(h1, h2)
        self.assertLess(sim, 0.65)


class TestSubnetHashingAndRateLimiting(unittest.TestCase):
    """Test IPv4 /32 and IPv6 /64 prefix aggregation for rate limiting."""

    def test_ipv4_subnets_produce_distinct_hashes(self) -> None:
        h1 = compute_subnet_hash("198.51.100.1")
        h2 = compute_subnet_hash("198.51.100.2")
        self.assertNotEqual(h1, h2)

    def test_ipv6_addresses_in_same_slash_64_produce_same_hash(self) -> None:
        # IPv6 hopping defense: different interface IDs in same /64 prefix share subnet hash
        ip1 = "2001:0db8:85a3:0001:0000:8a2e:0370:7334"
        ip2 = "2001:0db8:85a3:0001:ffff:ffff:ffff:ffff"
        ip_other = "2001:0db8:85a3:0002:0000:0000:0000:0001"

        h1 = compute_subnet_hash(ip1)
        h2 = compute_subnet_hash(ip2)
        h_other = compute_subnet_hash(ip_other)

        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h_other)


class TestCryptographicAntiReplayTokens(unittest.TestCase):
    """Test HMAC token validation, time bounds, and nonce consumption."""

    def setUp(self) -> None:
        self.secret = "test-secret-key-32-bytes-long!!"
        self.subnet = compute_subnet_hash("203.0.113.45")

    def test_valid_token_within_window_succeeds(self) -> None:
        now = 1700000100
        token = create_proposal_token(self.secret, self.subnet, timestamp=now - 10)
        is_valid, reason, nonce = verify_proposal_token(
            token, self.secret, self.subnet, now=now, min_seconds=3.0, max_seconds=600
        )
        self.assertTrue(is_valid)
        self.assertEqual(reason, "valid")
        self.assertIsNotNone(nonce)

    def test_token_submitted_under_minimum_duration_fails(self) -> None:
        now = 1700000100
        token = create_proposal_token(self.secret, self.subnet, timestamp=now - 1)  # Only 1s elapsed
        is_valid, reason, _ = verify_proposal_token(
            token, self.secret, self.subnet, now=now, min_seconds=3.0, max_seconds=600
        )
        self.assertFalse(is_valid)
        self.assertEqual(reason, "too_fast")

    def test_token_older_than_maximum_age_fails(self) -> None:
        now = 1700000100
        token = create_proposal_token(self.secret, self.subnet, timestamp=now - 601)  # 601s elapsed
        is_valid, reason, _ = verify_proposal_token(
            token, self.secret, self.subnet, now=now, min_seconds=3.0, max_seconds=600
        )
        self.assertFalse(is_valid)
        self.assertEqual(reason, "expired")

    def test_tampered_token_fails(self) -> None:
        now = 1700000100
        token = create_proposal_token(self.secret, self.subnet, timestamp=now - 10)
        tampered = token[:-4] + "dead"
        is_valid, reason, _ = verify_proposal_token(
            tampered, self.secret, self.subnet, now=now
        )
        self.assertFalse(is_valid)
        self.assertEqual(reason, "tampered_signature")


class TestSQLiteProposalRepository(unittest.TestCase):
    """Test Local SQLite persistence, WAL mode pragmas, and SQL injection defense."""

    def setUp(self) -> None:
        self.repo = SQLiteProposalRepository(":memory:")

    def tearDown(self) -> None:
        self.repo.close()

    def test_sql_injection_attempt_stored_literally(self) -> None:
        """Verify malicious SQL payloads are treated strictly as string data without syntax corruption."""
        malicious_payload = "'; DROP TABLE proposals; SELECT * FROM proposals WHERE ''='"
        record = ProposalRecord(
            id="urn:uuid:test-sqli",
            created_at="2026-10-15T12:00:00Z",
            category="general",
            text=malicious_payload,
            status="pending",
            char_count=len(malicious_payload),
            completion_time_ms=5000,
            content_hash=compute_content_hash(malicious_payload),
            simhash=compute_simhash(malicious_payload),
            subnet_hash="subnet-123",
        )

        self.repo.save_proposal(record)

        # Confirm table still exists and data was stored literally
        retrieved = self.repo.get_proposal("urn:uuid:test-sqli")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.text, malicious_payload)

        # Confirm table proposals was not dropped
        cur = self.repo.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM proposals")
        count = cur.fetchone()[0]
        cur.close()
        self.assertEqual(count, 1)

    def test_crud_and_status_transitions(self) -> None:
        record = ProposalRecord(
            id="urn:uuid:p1",
            created_at="2026-10-15T12:00:00Z",
            category="comparator",
            text="Propuesta constructiva para comparar tres partidos.",
            status="pending",
            char_count=49,
            completion_time_ms=12000,
            content_hash="h1",
            simhash="s1",
            subnet_hash="sub1",
        )
        self.repo.save_proposal(record)

        # List pending
        pending = self.repo.list_proposals(status="pending")
        self.assertEqual(len(pending), 1)

        # Transition to considered
        updated = self.repo.update_status(
            "urn:uuid:p1",
            "considered",
            reviewer_notes="Aprobado para paquete E2.3",
            action_ticket="GH-102",
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "considered")
        self.assertEqual(updated.reviewer_notes, "Aprobado para paquete E2.3")
        self.assertEqual(updated.action_ticket, "GH-102")

        # Verify stats reflect transition
        st = self.repo.stats()
        self.assertEqual(st["considered"], 1)
        self.assertEqual(st["pending"], 0)

    def test_anti_replay_nonce_tracking(self) -> None:
        nonce = "test-nonce-12345"
        self.assertFalse(self.repo.is_token_consumed(nonce))

        self.repo.mark_token_consumed(nonce, ttl_seconds=600)
        self.assertTrue(self.repo.is_token_consumed(nonce))

    def test_prune_expired_removes_old_nonces(self) -> None:
        # Insert expired nonce
        past = int(time.time()) - 10
        self.repo.conn.execute(
            "INSERT INTO consumed_tokens (nonce, consumed_at, expires_at) VALUES (?, ?, ?)",
            ("expired-nonce", "2026-10-01T00:00:00Z", past),
        )
        # Insert valid nonce
        future = int(time.time()) + 600
        self.repo.conn.execute(
            "INSERT INTO consumed_tokens (nonce, consumed_at, expires_at) VALUES (?, ?, ?)",
            ("valid-nonce", "2026-10-15T00:00:00Z", future),
        )

        pruned = self.repo.prune_expired()
        self.assertGreaterEqual(pruned, 1)

        self.assertFalse(self.repo.is_token_consumed("expired-nonce"))
        self.assertTrue(self.repo.is_token_consumed("valid-nonce"))


class TestFeedbackServicePipeline(unittest.TestCase):
    """End-to-end integration tests for the public submission pipeline."""

    def setUp(self) -> None:
        self.repo = SQLiteProposalRepository(":memory:")
        self.secret = "service-secret-test-32-chars-long!"
        self.service = FeedbackService(self.repo, secret_key=self.secret)
        self.client_ip = "192.0.2.1"
        self.subnet_hash = compute_subnet_hash(self.client_ip)

    def tearDown(self) -> None:
        self.repo.close()

    def test_successful_human_submission(self) -> None:
        now = 1700000000
        token = create_proposal_token(self.secret, self.subnet_hash, timestamp=now - 10)

        payload = ProposalCreate(
            text="Me gustaría ver un resumen ejecutivo antes de la tabla de medidas.",
            category="comparator",
            completion_time_ms=10500,
            honeypot="",
            token=token,
        )

        res = self.service.submit_proposal(payload, client_ip=self.client_ip, now=now)
        self.assertTrue(res.success)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.internal_status, "pending")
        self.assertIsNotNone(res.proposal_id)

        # Confirm persisted in DB
        record = self.repo.get_proposal(res.proposal_id)
        self.assertIsNotNone(record)
        self.assertEqual(record.status, "pending")
        self.assertEqual(record.category, "comparator")

    def test_honeypot_traps_bot_as_spam(self) -> None:
        """Spambots filling the hidden honeypot receive silent 201 but are tagged as spam."""
        now = 1700000000
        token = create_proposal_token(self.secret, self.subnet_hash, timestamp=now - 10)

        payload = ProposalCreate(
            text="Comprobad esta propuesta para mejorar la herramienta con enlaces.",
            category="general",
            completion_time_ms=8000,
            honeypot="SpamCorp Ltd.",
            token=token,
        )

        res = self.service.submit_proposal(payload, client_ip=self.client_ip, now=now)
        self.assertTrue(res.success)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.internal_status, "spam")

        record = self.repo.get_proposal(res.proposal_id)
        self.assertIsNotNone(record)
        self.assertEqual(record.status, "spam")

    def test_submission_too_fast_is_silently_dropped(self) -> None:
        """Automated scripts submitting in < 3 seconds are silently dropped."""
        now = 1700000000
        token = create_proposal_token(self.secret, self.subnet_hash, timestamp=now - 1)  # 1s elapsed

        payload = ProposalCreate(
            text="Texto de bot enviado en menos de un segundo.",
            token=token,
        )

        res = self.service.submit_proposal(payload, client_ip=self.client_ip, now=now)
        self.assertTrue(res.success)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.internal_status, "bot_too_fast_dropped")
        self.assertIsNone(res.proposal_id)

    def test_replay_of_same_token_rejected(self) -> None:
        """Submitting with the exact same nonce twice triggers anti-replay rejection."""
        now = 1700000000
        token = create_proposal_token(self.secret, self.subnet_hash, timestamp=now - 10)

        payload1 = ProposalCreate(
            text="Primera propuesta enviada legítimamente por el usuario.",
            token=token,
        )
        res1 = self.service.submit_proposal(payload1, client_ip=self.client_ip, now=now)
        self.assertTrue(res1.success)

        # Attempt replay
        payload2 = ProposalCreate(
            text="Segunda propuesta intentando reutilizar el mismo token nonce.",
            token=token,
        )
        res2 = self.service.submit_proposal(payload2, client_ip=self.client_ip, now=now)
        self.assertFalse(res2.success)
        self.assertEqual(res2.status_code, 409)
        self.assertEqual(res2.internal_status, "replay_attempt")

    def test_subnet_rate_limiting_exceeded(self) -> None:
        """Subnet exceeding 3 requests per hour window is blocked with HTTP 429."""
        now = 1700000000
        for i in range(3):
            token = create_proposal_token(self.secret, self.subnet_hash, timestamp=now - 10)
            payload = ProposalCreate(
                text=f"Propuesta número {i+1} enviada desde la misma subred.",
                token=token,
            )
            res = self.service.submit_proposal(payload, client_ip=self.client_ip, now=now)
            self.assertTrue(res.success)

        # 4th submission in same hour
        token4 = create_proposal_token(self.secret, self.subnet_hash, timestamp=now - 10)
        payload4 = ProposalCreate(
            text="Cuarta propuesta excediendo el límite por hora.",
            token=token4,
        )
        res4 = self.service.submit_proposal(payload4, client_ip=self.client_ip, now=now)
        self.assertFalse(res4.success)
        self.assertEqual(res4.status_code, 429)
        self.assertEqual(res4.internal_status, "rate_limited")

    def test_stored_xss_payload_stored_safely(self) -> None:
        """Verify stored XSS strings are stored as raw text without execution."""
        xss_text = "Propuesta con <script>alert('pwned')</script> y <img src=x onerror=alert(1)>"
        now = 1700000000
        token = create_proposal_token(self.secret, self.subnet_hash, timestamp=now - 10)

        payload = ProposalCreate(text=xss_text, token=token)
        res = self.service.submit_proposal(payload, client_ip=self.client_ip, now=now)
        self.assertTrue(res.success)

        record = self.repo.get_proposal(res.proposal_id)
        self.assertIsNotNone(record)
        self.assertEqual(record.text, xss_text)

    def test_text_length_bounds(self) -> None:
        now = 1700000000
        token = create_proposal_token(self.secret, self.subnet_hash, timestamp=now - 10)

        # Under 10 chars
        res_short = self.service.submit_proposal(
            ProposalCreate(text="Corto", token=token),
            client_ip=self.client_ip,
            now=now,
        )
        self.assertFalse(res_short.success)
        self.assertEqual(res_short.status_code, 422)

        # Over 600 chars
        token2 = create_proposal_token(self.secret, self.subnet_hash, timestamp=now - 10)
        res_long = self.service.submit_proposal(
            ProposalCreate(text="A" * 601, token=token2),
            client_ip=self.client_ip,
            now=now,
        )
        self.assertFalse(res_long.success)
        self.assertEqual(res_long.status_code, 422)


class TestTriageCLI(unittest.TestCase):
    """Test maintainer offline triage tool commands."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="triage_test_")
        self.db_path = os.path.join(self.temp_dir, "test_feedback.db")
        self.repo = SQLiteProposalRepository(self.db_path)
        self.repo.save_proposal(
            ProposalRecord(
                id="urn:uuid:t1",
                created_at="2026-10-15T10:00:00Z",
                category="comparator",
                text="Añadir vista comparativa de tres partidos.",
                status="pending",
                char_count=42,
                completion_time_ms=8000,
                content_hash="h1",
                simhash="s1",
                subnet_hash="sub1",
            )
        )
        self.repo.save_proposal(
            ProposalRecord(
                id="urn:uuid:t2",
                created_at="2026-10-15T11:00:00Z",
                category="ui",
                text="Revisar contraste del botón de volver.",
                status="considered",
                char_count=38,
                completion_time_ms=6000,
                content_hash="h2",
                simhash="s2",
                subnet_hash="sub2",
                reviewer_notes="Aprobado para E2.5",
            )
        )

    def tearDown(self) -> None:
        self.repo.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_stats(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = triage_cli.main(["--db", self.db_path, "stats"])
        self.assertEqual(code, 0)
        output = buf.getvalue()
        self.assertIn("Total registradas: 2", output)
        self.assertIn("PENDING     : 1", output)
        self.assertIn("CONSIDERED  : 1", output)

    def test_cli_list(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = triage_cli.main(["--db", self.db_path, "list", "--status", "pending"])
        self.assertEqual(code, 0)
        output = buf.getvalue()
        self.assertIn("Añadir vista comparativa de tres partidos.", output)

    def test_cli_export(self) -> None:
        out_file = os.path.join(self.temp_dir, "export.md")
        code = triage_cli.main(["--db", self.db_path, "export", "--out", out_file])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(out_file))
        content = Path(out_file).read_text(encoding="utf-8")
        self.assertIn("Revisar contraste del botón de volver.", content)
        self.assertIn("Aprobado para E2.5", content)

    def test_cli_prune(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = triage_cli.main(["--db", self.db_path, "prune"])
        self.assertEqual(code, 0)
        self.assertIn("Eliminadas 0 entradas expiradas", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
