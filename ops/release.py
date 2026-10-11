#!/usr/bin/env python3
"""Switch approved immutable images; recover the last image on failed health checks."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import time

COMPOSE = Path(__file__).with_name("compose.yaml")
IMAGE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._:/-]*@sha256:[a-f0-9]{64}\Z")


def validate_image(image):
    if not isinstance(image, str) or not IMAGE.fullmatch(image):
        raise ValueError("Release image must use an immutable sha256 digest")
    return image


def compose(image, *args):
    env = dict(os.environ, RELEASE_IMAGE=validate_image(image))
    return subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE), *args],
        env=env, check=True, capture_output=True, text=True,
    ).stdout.strip()


def activate(image):
    port = int(os.environ.get("ELECTIONS_ORIGIN_PORT", "8080"))
    if not 1 <= port <= 65535:
        raise ValueError("Invalid loopback port")
    compose(image, "up", "-d", "--no-build", "--pull", "never", "--wait", "--wait-timeout", "60")
    container = compose(image, "ps", "-q", "site")
    if not container:
        raise RuntimeError("Serving container is missing")
    # Container health alone is insufficient: check the published loopback route.
    subprocess.run(
        ["curl", "--fail", "--silent", "--show-error", "--max-time", "10",
         "--output", "/dev/null", f"http://127.0.0.1:{port}/"], check=True,
        capture_output=True,
    )


def switch(state_dir, image=None, rollback=False):
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state_dir / "release.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state_file = state_dir / "release.json"
        state = json.loads(state_file.read_text()) if state_file.exists() else {}
        current = state.get("current")
        if current:
            validate_image(current)
        target = validate_image(state.get("previous") if rollback else image)
        if target == current:
            if rollback:
                raise ValueError("Rollback target is already current")
            # A retry after an edge failure must still verify origin health without
            # replacing the retained rollback image or requiring registry access.
            started = time.monotonic()
            activate(target)
            return time.monotonic() - started
        # Pull before touching the running container. Retain the current image locally.
        if rollback:
            # Registry availability must not block recovery of a retained image.
            local = subprocess.run(["docker", "image", "inspect", target],
                                   capture_output=True, check=False)
            if local.returncode:
                compose(target, "pull", "site")
        else:
            compose(target, "pull", "site")
        started = time.monotonic()
        try:
            activate(target)
            temporary = state_dir / "release.json.tmp"
            temporary.write_text(json.dumps({"current": target, "previous": current}) + "\n")
            temporary.replace(state_file)
        except Exception:
            if current:
                activate(current)
            else:
                compose(target, "down")
            raise
        return time.monotonic() - started


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=Path("/var/lib/elecciones2026"))
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--image")
    action.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    try:
        elapsed = switch(args.state_dir, args.image, args.rollback)
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Release failed ({type(error).__name__}); inspect local Docker health.\n")
    print(f"Healthy origin release; switch took {elapsed:.1f}s. Verify edge and purge mutable URLs.")


if __name__ == "__main__":
    main()
