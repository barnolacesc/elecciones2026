#!/usr/bin/python3
"""Validate a narrow release request before invoking root-owned Docker tooling."""
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

INSTALL_DIR = Path("/opt/elecciones2026")
STATE_DIR = Path("/var/lib/elecciones2026")
REPOSITORIES = ("ghcr.io/c2ventures/elecciones2026", "ghcr.io/barnolacesc/elecciones2026")
# Retain the legacy namespace while approved rollback images still use it.
DEPLOY = re.compile(r"deploy ((?:" + "|".join(map(re.escape, REPOSITORIES))
                   + r")@sha256:[a-f0-9]{64})\Z")
ENVIRONMENT = {
    "HOME": "/root",
    "PATH": "/usr/bin:/bin",
    "LC_ALL": "C",
    "DOCKER_CONFIG": "/root/.docker",
    "DOCKER_HOST": "unix:///var/run/docker.sock",
    "COMPOSE_PROJECT_NAME": "elecciones2026-production",
    "ELECTIONS_ORIGIN_PORT": "8080",
}


def parse_request(arguments):
    """Accept one literal request, without tokenization or shell evaluation."""
    if len(arguments) != 1:
        raise ValueError("Exactly one release request is required")
    request = arguments[0]
    if request == "check":
        return []
    if request == "rollback":
        return ["--rollback"]
    match = DEPLOY.fullmatch(request)
    if not match:
        raise ValueError("Release request is not allowed")
    return ["--image", match.group(1)]


def require_root_owned(path, directory=False):
    """Reject symlinks, non-root ownership and write access along the full path."""
    for item in [path, *path.parents]:
        info = item.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise ValueError("Deployment paths must not contain symlinks")
        if info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError("Deployment paths must be root-owned and protected")
        is_directory = item != path or directory
        if is_directory and not stat.S_ISDIR(info.st_mode):
            raise ValueError("Deployment directory is invalid")
        if not is_directory and not stat.S_ISREG(info.st_mode):
            raise ValueError("Deployment file is invalid")


def validate_installation():
    require_root_owned(INSTALL_DIR, directory=True)
    for name in ("restricted_release.py", "release.py", "compose.yaml"):
        require_root_owned(INSTALL_DIR / name)
    require_root_owned(STATE_DIR, directory=True)
    for name in ("release.json", "release.lock", "release.json.tmp"):
        path = STATE_DIR / name
        # lexists also detects dangling symlinks.
        if os.path.lexists(path):
            require_root_owned(path)
    record = STATE_DIR / "release.json"
    if record.exists():
        state = json.loads(record.read_text())
        if not isinstance(state, dict):
            raise ValueError("Release state is invalid")
        for name in ("current", "previous"):
            image = state.get(name)
            if image is not None and (not isinstance(image, str) or
                                      not DEPLOY.fullmatch("deploy " + image)):
                raise ValueError("Retained image repository is not allowed")


def execute(arguments):
    action = parse_request(arguments)
    if os.geteuid() != 0:
        raise ValueError("Release wrapper requires its configured sudo permission")
    validate_installation()
    if not action:
        print("Restricted release access ready; no deployment performed.")
        return
    os.umask(0o077)
    subprocess.run(
        ["/usr/bin/python3", "-I", str(INSTALL_DIR / "release.py"),
         "--state-dir", str(STATE_DIR), *action],
        env=ENVIRONMENT.copy(), cwd=INSTALL_DIR, stdin=subprocess.DEVNULL,
        check=True,
    )


def main():
    try:
        execute(sys.argv[1:])
    except (ValueError, OSError, subprocess.CalledProcessError):
        # Do not echo rejected requests, environment values or registry errors.
        print("Release request refused or failed; inspect root-owned operations locally.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
