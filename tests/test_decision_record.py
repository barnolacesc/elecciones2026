"""Tests for project decision record (ADR-0001 / Package E0.3).

Verifies the required decisions on language, domain, privacy notice, release
service levels, cost ceiling, and role ownership are codified and referenced.
"""

from pathlib import Path
import re
import unittest


class TestDecisionRecord(unittest.TestCase):
    """Verify contents and consistency of the E0.3 decision record."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.decision_record_path = cls.repo_root / "docs" / "DECISION-RECORD.md"
        cls.architecture_path = cls.repo_root / "docs" / "ARCHITECTURE.md"
        cls.security_path = cls.repo_root / "docs" / "SECURITY.md"
        cls.tasks_path = (
            cls.repo_root
            / "openspec"
            / "changes"
            / "mvp-programme-comparison"
            / "tasks.md"
        )

        cls.decision_record_text = cls.decision_record_path.read_text(
            encoding="utf-8"
        )
        cls.architecture_text = cls.architecture_path.read_text(encoding="utf-8")
        cls.security_text = cls.security_path.read_text(encoding="utf-8")
        cls.tasks_text = cls.tasks_path.read_text(encoding="utf-8")

    def test_decision_record_exists_and_identified(self):
        self.assertTrue(
            self.decision_record_path.is_file(),
            "docs/DECISION-RECORD.md must exist",
        )
        self.assertIn("ADR-0001", self.decision_record_text)
        self.assertIn("E0.3", self.decision_record_text)

    def test_language_governance_defined(self):
        text = self.decision_record_text
        self.assertIn("es-ES", text, "Spanish public language must be defined")
        self.assertIn("Controlled Technical English", text)
        self.assertIn("ASD-STE100", text)
        self.assertIn("<html lang=\"es\">", text)
        self.assertIn("ca-ES", text, "Catalan localization must be referenced")

    def test_domain_and_dns_architecture_defined(self):
        text = self.decision_record_text
        self.assertIn("elecciones2026.es", text, "Primary canonical domain must be defined")
        self.assertIn("elecciones2026.org", text, "Defensive domain must be defined")
        self.assertIn("programaselectorales.es", text, "Defensive domain must be defined")
        self.assertIn("preview.elecciones2026.es", text, "Staging domain must be defined")
        self.assertIn("301", text, "Permanent 301 redirects must be required")
        self.assertIn("DNSSEC", text, "DNSSEC must be specified")
        self.assertIn("Cloudflare", text, "Cloudflare DNS/proxy must be specified")
        self.assertIn("placeholder", text.lower(), "Domain documentation must note placeholder status pending acquisition")

    def test_privacy_notice_and_data_minimization_defined(self):
        text = self.decision_record_text
        self.assertIn("GDPR", text)
        self.assertIn("LOPDGDD", text)
        self.assertIn("C2 Ventures", text, "Data controller must be identified")
        self.assertIn("privacidad@elecciones2026.es", text, "Privacy contact must be specified")
        self.assertIn("14 days", text, "Maximum log retention of 14 days must be defined")
        self.assertIn("Aviso de Privacidad", text, "Spanish privacy notice text must be present")
        self.assertIn("Agencia Española de Protección de Datos", text)

    def test_service_level_objectives_quantified(self):
        text = self.decision_record_text
        # Availability
        self.assertIn("99.5%", text, "Monthly availability SLO must be >= 99.5%")
        self.assertIn("99.9%", text, "Election week availability SLO must be >= 99.9%")

        # Latency p95 targets
        self.assertIn("150 ms", text, "Edge p95 latency target must be < 150 ms")
        self.assertIn("250 ms", text, "Origin p95 latency target must be < 250 ms")
        self.assertIn("500 ms", text, "Mobile p95 delivery target must be < 500 ms")

        # Cache-hit ratio targets
        self.assertIn("99.0%", text, "Static asset edge cache hit ratio target must be >= 99.0%")
        self.assertIn("90.0%", text, "HTML document edge cache hit ratio target must be >= 90.0%")
        self.assertIn("95.0%", text, "Aggregate steady-state edge cache hit ratio target must be >= 95.0%")
        self.assertIn("85.0%", text, "Cold-cache recovery edge cache hit ratio target must be >= 85.0%")

        # Error budget targets
        self.assertIn("0.05%", text, "HTTP 5xx error rate steady target must be < 0.05%")
        self.assertIn("0.50%", text, "HTTP 5xx error rate burst target must be < 0.50%")

        # Recovery targets
        self.assertIn("RTO", text)
        self.assertIn("RPO", text)
        self.assertIn("5 minutes", text)

    def test_concurrency_and_capacity_scenario_modeled(self):
        text = self.decision_record_text
        self.assertIn("10,000", text, "10,000 concurrent visitors scenario must be modeled")
        self.assertIn("2-vCPU", text)
        self.assertIn("8-GB", text)

    def test_cost_ceiling_and_governance_defined(self):
        text = self.decision_record_text
        self.assertIn("€50.00", text, "Hard cost ceiling of €50.00/month must be defined")
        self.assertIn("€25.00", text, "Warning threshold alert at €25.00 must be defined")
        self.assertIn("€40.00", text, "Critical threshold alert at €40.00 must be defined")

    def test_named_owners_matrix_defined(self):
        text = self.decision_record_text
        self.assertIn("Cesc", text, "Infrastructure & Operations Owner must be assigned")
        self.assertIn("Release Engineering Lead", text, "Security/Release Gatekeeper must be assigned")
        self.assertIn("Project Partner", text, "Editorial owner must be assigned")

    def test_cross_document_consistency(self):
        # ARCHITECTURE.md consistency
        self.assertIn(
            "DECISION-RECORD.md",
            self.architecture_text,
            "ARCHITECTURE.md must reference DECISION-RECORD.md",
        )
        self.assertIn("xn--eleccionesespaa2026-83b.es", self.architecture_text)
        self.assertIn("€50.00", self.architecture_text)
        self.assertIn("150 ms", self.architecture_text)
        self.assertIn("250 ms", self.architecture_text)

        # SECURITY.md consistency
        self.assertIn(
            "DECISION-RECORD.md",
            self.security_text,
            "SECURITY.md must reference DECISION-RECORD.md",
        )
        self.assertIn("privacidad@elecciones2026.es", self.security_text)
        self.assertIn("seguridad@elecciones2026.es", self.security_text)
        self.assertIn("14 days", self.security_text)

        # tasks.md consistency for tasks 4.3, 4.6, 4.7
        self.assertIn("4.3", self.tasks_text)
        self.assertIn("4.6", self.tasks_text)
        self.assertIn("4.7", self.tasks_text)
        self.assertIn("DECISION-RECORD.md", self.tasks_text)


if __name__ == "__main__":
    unittest.main()
