"""Exercise the privileged boundary without host credentials or deployment."""
import importlib.util
from pathlib import Path
import stat
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("restricted_release", ROOT / "ops/restricted_release.py")
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)
IMAGE = wrapper.REPOSITORIES[0] + "@sha256:" + "a" * 64


class RestrictedReleaseTests(unittest.TestCase):
    def test_transition_accepts_both_exact_namespaces_and_mixed_rollback_state(self):
        import json
        images = [repository + '@sha256:' + 'a' * 64 for repository in wrapper.REPOSITORIES]
        for image in images:
            self.assertEqual(wrapper.parse_request(['deploy ' + image]), ['--image', image])
            for invalid in (image.replace('/elecciones2026@', '/elecciones2026-copy@'),
                            image.replace('@sha256:', ':latest@sha256:'),
                            image.replace('ghcr.io/', 'ghcr.io/other/')):
                with self.subTest(image=invalid), self.assertRaises(ValueError):
                    wrapper.parse_request(['deploy ' + invalid])
        with patch.object(wrapper, 'require_root_owned'), \
                patch.object(wrapper.os.path, 'lexists', return_value=True), \
                patch.object(Path, 'exists', return_value=True), \
                patch.object(Path, 'read_text', return_value=json.dumps(
                    {'current': images[1], 'previous': images[0]})):
            wrapper.validate_installation()

    def test_only_exact_actions_and_allowlisted_digest_are_accepted(self):
        self.assertEqual(wrapper.parse_request(["deploy " + IMAGE]), ["--image", IMAGE])
        self.assertEqual(wrapper.parse_request(["rollback"]), ["--rollback"])
        self.assertEqual(wrapper.parse_request(["check"]), [])
        rejected = [
            [], ["deploy", IMAGE], ["check", "extra"], [""], ["bash"],
            [" deploy " + IMAGE], ["deploy " + IMAGE + "\n"],
            ["deploy " + IMAGE + "; id"], ["deploy $(id)"],
            ["deploy `id`"], ["deploy " + IMAGE + " --state-dir /tmp"],
            ["deploy " + IMAGE.replace(wrapper.REPOSITORIES[0], "ghcr.io/other/site")],
            ["deploy " + wrapper.REPOSITORIES[0] + ":latest"],
            ["deploy " + wrapper.REPOSITORIES[0] + "@sha256:" + "A" * 64],
            ["rollback\n"], ["deploy\t" + IMAGE], ["check\x00"],
        ]
        with patch.object(wrapper, "validate_installation") as validate, \
                patch.object(wrapper.subprocess, "run") as run:
            for arguments in rejected:
                with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                    wrapper.execute(arguments)
            validate.assert_not_called()
            run.assert_not_called()

    def test_non_root_is_rejected(self):
        with patch.object(wrapper.os, "geteuid", return_value=1000), \
                patch.object(wrapper.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                wrapper.execute(["deploy " + IMAGE])
            run.assert_not_called()

    def test_controller_has_fixed_paths_arguments_and_clean_environment(self):
        hostile = {"PYTHONPATH": "/tmp/evil", "COMPOSE_FILE": "/tmp/evil.yml",
                   "DOCKER_HOST": "tcp://evil:2375", "HOME": "/tmp/evil",
                   "ELECTIONS_ORIGIN_PORT": "22", "LD_PRELOAD": "/tmp/evil.so"}
        with patch.dict(wrapper.os.environ, hostile), \
                patch.object(wrapper.os, "geteuid", return_value=0), \
                patch.object(wrapper.os, "umask") as umask, \
                patch.object(wrapper, "validate_installation"), \
                patch.object(wrapper.subprocess, "run") as run:
            wrapper.execute(["deploy " + IMAGE])
            args, kwargs = run.call_args
            self.assertEqual(args[0], ["/usr/bin/python3", "-I",
                             "/opt/elecciones2026/release.py", "--state-dir",
                             "/var/lib/elecciones2026", "--image", IMAGE])
            self.assertEqual(kwargs["env"], wrapper.ENVIRONMENT)
            self.assertNotIn("PYTHONPATH", kwargs["env"])
            self.assertNotIn("COMPOSE_FILE", kwargs["env"])
            self.assertNotIn("LD_PRELOAD", kwargs["env"])
            self.assertEqual(kwargs["cwd"], Path("/opt/elecciones2026"))
            self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
            self.assertTrue(kwargs["check"])
            umask.assert_called_once_with(0o077)

    def test_check_does_not_deploy_and_failure_propagates(self):
        with patch.object(wrapper.os, "geteuid", return_value=0), \
                patch.object(wrapper, "validate_installation"), \
                patch.object(wrapper.subprocess, "run") as run:
            wrapper.execute(["check"])
            run.assert_not_called()
            run.side_effect = subprocess.CalledProcessError(1, "controller")
            with patch.object(wrapper.os, "umask"), self.assertRaises(subprocess.CalledProcessError):
                wrapper.execute(["rollback"])

    def test_path_ownership_permissions_symlinks_and_types(self):
        file = Path("/opt/elecciones2026/release.py")
        def safe_info(path):
            kind = stat.S_IFREG if path == file else stat.S_IFDIR
            return SimpleNamespace(st_uid=0, st_mode=kind | 0o755)
        with patch.object(Path, "lstat", autospec=True, side_effect=safe_info):
            wrapper.require_root_owned(file)
        for location in (file, file.parent, Path("/opt"), Path("/")):
            for uid, mode in ((1000, stat.S_IFREG | 0o644),
                              (0, stat.S_IFREG | 0o666),
                              (0, stat.S_IFLNK | 0o777)):
                def bad_info(path):
                    return SimpleNamespace(st_uid=uid, st_mode=mode) if path == location else safe_info(path)
                with self.subTest(location=location, uid=uid, mode=mode), \
                        patch.object(Path, "lstat", autospec=True, side_effect=bad_info), \
                        self.assertRaises(ValueError):
                    wrapper.require_root_owned(file)
        with patch.object(Path, "lstat", return_value=SimpleNamespace(st_uid=0, st_mode=stat.S_IFDIR | 0o755)), \
                self.assertRaises(ValueError):
            wrapper.require_root_owned(file)

    def test_state_artifacts_including_dangling_links_are_checked(self):
        with patch.object(wrapper, "require_root_owned") as check, \
                patch.object(wrapper.os.path, "lexists", return_value=True), \
                patch.object(Path, "exists", return_value=False):
            wrapper.validate_installation()
            paths = [call.args[0] for call in check.call_args_list]
            self.assertIn(wrapper.STATE_DIR / "release.lock", paths)
            self.assertIn(wrapper.STATE_DIR / "release.json.tmp", paths)
            self.assertIn(wrapper.INSTALL_DIR / "compose.yaml", paths)

    def test_rollback_cannot_use_foreign_or_malformed_retained_images(self):
        import json
        for record in ({"current": IMAGE, "previous": "other/site@sha256:" + "b" * 64},
                       {"current": "site:latest"}, {"current": 3}, []):
            with self.subTest(record=record), \
                    patch.object(wrapper, "require_root_owned"), \
                    patch.object(wrapper.os.path, "lexists", return_value=True), \
                    patch.object(Path, "exists", return_value=True), \
                    patch.object(Path, "read_text", return_value=json.dumps(record)), \
                    self.assertRaises(ValueError):
                wrapper.validate_installation()

    def test_shell_launchers_preserve_one_argument_and_do_not_inherit_overrides(self):
        # Execute both actual launchers against a recording env binary, without sudo.
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            recorder = Path(temporary) / "record.py"
            recorder.write_text("import json,sys; print(json.dumps(sys.argv[1:]))")
            import json
            import sys
            import shlex
            prefix = shlex.quote(sys.executable) + " " + shlex.quote(str(recorder))
            for name in ("elecciones-ssh", "elecciones-release"):
                source = (ROOT / "ops" / name).read_text().replace("/usr/bin/env", prefix)
                script = Path(temporary) / name
                script.write_text(source)
                request = "deploy " + IMAGE + "; touch /tmp/forbidden"
                result = subprocess.run(["/bin/sh", str(script), request],
                                        env={"SSH_ORIGINAL_COMMAND": request, "PYTHONPATH": "/tmp/evil"},
                                        capture_output=True, text=True, check=True)
                arguments = json.loads(result.stdout)
                self.assertEqual(arguments[0], "-i")
                self.assertEqual(arguments[-1], request)
                self.assertEqual(arguments.count(request), 1)
                self.assertNotIn("PYTHONPATH=/tmp/evil", arguments)


if __name__ == "__main__":
    unittest.main()
