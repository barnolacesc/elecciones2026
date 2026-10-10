"""Tests for CI least-privilege, fork PR secret isolation, and security boundaries (Package E3.2).

Verifies acceptance criteria for OpenSpec tasks 4.1 and 4.2:
- CI workflow permissions enforce least privilege (permissions: contents: read).
- Fork pull requests cannot access deployment secrets or run untrusted deployment steps.
- Dangerous triggers (pull_request_target) are strictly forbidden.
- Zero committed secrets or API tokens exist in the repository.
- Dependency inventory and security advisory audit are documented.
"""

from __future__ import annotations

import os
import re
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = ROOT_DIR / ".github" / "workflows"
DEPENDENCY_AUDIT_PATH = ROOT_DIR / "docs" / "DEPENDENCY-AUDIT.md"

PROHIBITED_SECRET_PATTERNS = [
    (r"-----BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----", "Private key header"),
    (r"(?:api[_-]?key|secret[_-]?key|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]", "API key or secret"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token"),
    (r"github_pat_[A-Za-z0-9_]{82}", "Fine-grained GitHub Personal Access Token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"CLOUDFLARE_API_TOKEN\s*=\s*['\"][^'\"]+['\"]", "Cloudflare API token assignment"),
]


class TestCISecurity(unittest.TestCase):
    """Test suite for CI least-privilege policies, secret protection, and dependency safety."""

    def test_workflows_exist_and_use_least_privilege_permissions(self) -> None:
        """Verify all GitHub Actions workflows declare top-level read-only permissions."""
        self.assertTrue(WORKFLOWS_DIR.is_dir(), f"Missing workflows directory at {WORKFLOWS_DIR}")
        workflow_files = list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))
        self.assertGreater(len(workflow_files), 0, "At least one workflow must be defined")

        for wf in workflow_files:
            content = wf.read_text(encoding="utf-8")

            # Must declare top-level permissions: contents: read
            self.assertRegex(
                content,
                r"permissions:\s+(?:contents:\s+read|read-all)",
                f"Workflow {wf.name} must declare least-privilege permissions (contents: read)",
            )

            # Must NEVER use pull_request_target (critical vulnerability vector for forks)
            self.assertNotIn(
                "pull_request_target",
                content,
                f"Workflow {wf.name} MUST NOT use dangerous 'pull_request_target' trigger",
            )

    def test_fork_prs_cannot_access_deploy_secrets(self) -> None:
        """Verify fork PRs have no path to access deploy credentials or trigger releases."""
        ci_workflow = WORKFLOWS_DIR / "ci.yml"
        self.assertTrue(ci_workflow.is_file(), f"Missing CI workflow at {ci_workflow}")
        content = ci_workflow.read_text(encoding="utf-8")

        # The pull_request event triggers on branches: [main]
        # Verify any deploy or release step has explicit guards:
        # 1. PR-accessible jobs must not reference deployment secrets
        # Search for any secret references in steps
        secret_refs = re.findall(r"\$\{\{\s*secrets\.([A-Za-z0-9_]+)\s*\}\}", content)
        for secret_name in secret_refs:
            # If any secret is referenced, ensure it is guarded behind event != pull_request
            self.assertIn(
                "github.event_name != 'pull_request'",
                content,
                f"Secret '{secret_name}' referenced without fork PR exclusion check",
            )

    def test_no_secrets_or_private_keys_in_repository_files(self) -> None:
        """Verify absence of unencrypted API keys, private keys, or passwords across repo."""
        ignored_dirs = {".git", ".pytest_cache", "__pycache__", "dist", "node_modules"}

        for root, dirs, files in os.walk(ROOT_DIR):
            dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith(".tmp")]
            for fname in files:
                if fname.endswith((".pyc", ".png", ".jpg", ".pdf", ".lock")):
                    continue
                file_path = Path(root) / fname
                try:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                for pattern, desc in PROHIBITED_SECRET_PATTERNS:
                    match = re.search(pattern, text)
                    self.assertIsNone(
                        match,
                        f"Found prohibited {desc} in {file_path.relative_to(ROOT_DIR)}: {match.group(0) if match else ''}",
                    )

    def test_dependency_inventory_and_audit_documentation_present(self) -> None:
        """Verify Task 4.2 release evidence: dependency audit document exists and covers key criteria."""
        self.assertTrue(
            DEPENDENCY_AUDIT_PATH.is_file(),
            f"Missing dependency audit document at {DEPENDENCY_AUDIT_PATH}",
        )
        content = DEPENDENCY_AUDIT_PATH.read_text(encoding="utf-8")

        # Must cover key OpenSpec tasks and topics
        self.assertIn("4.1", content)
        self.assertIn("4.2", content)
        self.assertIn("4.5", content)
        self.assertIn("Zero Runtime Dependencies", content)
        self.assertIn("Zero Native PDF Parsers", content)
        self.assertIn("CVE-2026-4775", content)
        self.assertIn("Least-Privilege CI", content)

    def test_pure_standard_library_runtime_boundaries(self) -> None:
        """Verify pyproject.toml defines zero third-party runtime dependencies."""
        pyproject = ROOT_DIR / "pyproject.toml"
        self.assertTrue(pyproject.is_file())
        content = pyproject.read_text(encoding="utf-8")

        self.assertIn("dependencies = []", content, "Project runtime dependencies must remain empty")

        # Verify importer.py does not import external pdf libraries
        importer_path = ROOT_DIR / "src" / "elecciones2026" / "importer.py"
        importer_code = importer_path.read_text(encoding="utf-8")
        for bad_lib in ["pypdf", "pdfminer", "fitz", "poppler", "ghostscript"]:
            self.assertNotIn(f"import {bad_lib}", importer_code)
            self.assertNotIn(f"from {bad_lib}", importer_code)


if __name__ == "__main__":
    unittest.main()
