"""Exercise release failure recovery without production access or credentials."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release", ROOT / "ops/release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
A = "registry.example.invalid/site@sha256:" + "a" * 64
B = "registry.example.invalid/site@sha256:" + "b" * 64


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state_dir = Path(self.tmp.name)
        self.state = self.state_dir / "release.json"

    def seed(self):
        self.state.write_text(json.dumps({"current": A, "previous": B}))

    def test_success_retains_previous_and_rollback_restores_it(self):
        self.seed()
        with patch.object(release, "compose") as compose, patch.object(release, "activate") as activate:
            release.switch(self.state_dir, B)
            self.assertEqual(json.loads(self.state.read_text()), {"current": B, "previous": A})
            release.switch(self.state_dir, rollback=True)
            self.assertEqual(json.loads(self.state.read_text()), {"current": A, "previous": B})
            self.assertEqual([c.args for c in activate.call_args_list], [(B,), (A,)])
            self.assertEqual([c.args for c in compose.call_args_list], [(B, "pull", "site"), (A, "pull", "site")])

    def test_failed_health_restores_current_without_changing_record(self):
        self.seed()
        old = self.state.read_bytes()
        with patch.object(release, "compose"), patch.object(release, "activate", side_effect=[RuntimeError("unhealthy"), None]) as activate:
            with self.assertRaises(RuntimeError):
                release.switch(self.state_dir, B)
            self.assertEqual([c.args for c in activate.call_args_list], [(B,), (A,)])
        self.assertEqual(self.state.read_bytes(), old)

    def test_failed_pull_does_not_touch_running_release(self):
        self.seed()
        with patch.object(release, "compose", side_effect=subprocess.CalledProcessError(1, "docker")), patch.object(release, "activate") as activate:
            with self.assertRaises(subprocess.CalledProcessError):
                release.switch(self.state_dir, B)
            activate.assert_not_called()
        self.assertEqual(json.loads(self.state.read_text())["current"], A)

    def test_failed_first_release_is_removed(self):
        with patch.object(release, "compose") as compose, patch.object(release, "activate", side_effect=RuntimeError("unhealthy")):
            with self.assertRaises(RuntimeError):
                release.switch(self.state_dir, A)
            compose.assert_called_with(A, "down")
        self.assertFalse(self.state.exists())

    def test_missing_rollback_and_mutable_tags_are_rejected_before_docker(self):
        with patch.object(release, "compose") as compose:
            for image in ["site:latest", "site@sha256:abc", "--help", None]:
                with self.assertRaises(ValueError):
                    release.switch(self.state_dir, image)
            with self.assertRaises(ValueError):
                release.switch(self.state_dir, rollback=True)
            compose.assert_not_called()

    def test_failed_recovery_is_not_reported_as_success(self):
        self.seed()
        with patch.object(release, "compose"), patch.object(release, "activate", side_effect=RuntimeError("failure")):
            with self.assertRaises(RuntimeError):
                release.switch(self.state_dir, B)
        self.assertEqual(json.loads(self.state.read_text())["current"], A)

    def test_activation_checks_container_and_loopback_http(self):
        with patch.object(release, "compose", side_effect=["", "container-id"]) as compose, patch.object(release.subprocess, "run") as run:
            release.activate(A)
            self.assertIn("--wait", compose.call_args_list[0].args)
            self.assertIn("http://127.0.0.1:8080/", run.call_args.args[0])
            self.assertTrue(run.call_args.kwargs["check"])


if __name__ == "__main__":
    unittest.main()
