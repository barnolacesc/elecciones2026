#!/usr/bin/env python3
"""Local Docker rehearsal; never uses a production registry, domain, or credential."""
import argparse
import json
import os
import socket
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import urllib.request

import release


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Local rehearsal command failed: {args[0:2]}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def read_marker():
    return urllib.request.urlopen(f"http://127.0.0.1:{os.environ['ELECTIONS_ORIGIN_PORT']}/", timeout=5).read().decode().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-image", default="elecciones2026:ci")
    args = parser.parse_args()
    name = f"elections-ops-registry-{int(time.time())}"
    images = []
    tags = []
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        os.environ["ELECTIONS_ORIGIN_PORT"] = str(listener.getsockname()[1])
    with tempfile.TemporaryDirectory(prefix="elections-ops-") as directory:
        root = Path(directory)
        try:
            run("docker", "run", "-d", "--rm", "--name", name,
                "-p", "127.0.0.1::5000", "registry:2")
            port = json.loads(run("docker", "inspect", name))[0]["NetworkSettings"]["Ports"]["5000/tcp"][0]["HostPort"]
            registry = f"127.0.0.1:{port}"
            for attempt in range(30):
                try:
                    urllib.request.urlopen(f"http://{registry}/v2/", timeout=1).close()
                    break
                except OSError:
                    time.sleep(1)
            else:
                raise RuntimeError("Local registry did not start")
            for marker in ["release-a", "release-b", "unhealthy"]:
                (root / "index.html").write_text(marker)
                health = ""
                if marker == "unhealthy":
                    (root / "unhealthy.conf").write_text("server { listen 8080; location / { return 503; } }\n")
                    health = "COPY --chown=101:101 unhealthy.conf /etc/nginx/conf.d/default.conf\n"
                (root / "Dockerfile").write_text(
                    f"FROM {args.base_image}\nCOPY --chown=101:101 index.html /usr/share/nginx/html/index.html\n" + health
                )
                tag = f"{registry}/site:{marker}"
                run("docker", "build", "-t", tag, str(root))
                tags.append(tag)
                run("docker", "push", tag)
                digest = run("docker", "image", "inspect", "--format", "{{index .RepoDigests 0}}", tag)
                images.append((tag, digest))
            state_dir = root / "state"
            release.switch(state_dir, images[0][1])
            assert read_marker() == "release-a"
            release.switch(state_dir, images[1][1])
            assert read_marker() == "release-b"
            seconds = release.switch(state_dir, rollback=True)
            assert read_marker() == "release-a"
            assert seconds < 300, "Rollback exceeded RTO target"
            before = (state_dir / "release.json").read_bytes()
            try:
                release.switch(state_dir, images[2][1])
            except subprocess.CalledProcessError:
                pass
            else:
                raise AssertionError("Unhealthy image was accepted")
            assert read_marker() == "release-a"
            assert (state_dir / "release.json").read_bytes() == before
            # Validate host nginx syntax with disposable self-signed test material.
            run("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                "-keyout", str(root / "origin.key"), "-out", str(root / "origin.pem"),
                "-days", "1", "-subj", "/CN=election.example.invalid")
            shutil.copy(root / "origin.pem", root / "origin-pull-ca.pem")
            conf = root / "origin.conf"
            conf.write_text(Path(__file__).with_name("origin.conf").read_text())
            run("docker", "run", "--rm", "--user", "0", "--entrypoint", "nginx",
                "-v", f"{root}:/etc/elecciones2026/tls:ro",
                "-v", f"{conf}:/etc/nginx/conf.d/default.conf:ro", args.base_image, "-t")
            print(f"PASS: A -> B -> A rollback in {seconds:.1f}s; unhealthy image restored A; TLS proxy syntax valid")
        finally:
            if images:
                release.compose(images[0][1], "down")
            run("docker", "rm", "-f", name)
            for tag in tags:
                subprocess.run(["docker", "image", "rm", tag], capture_output=True)


if __name__ == "__main__":
    main()
