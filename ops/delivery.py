"""Validate trusted CI evidence and deliver an authenticated staging release (E3.3)."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.error
import urllib.request

REPOSITORY = "c2ventures/elecciones2026"
IMAGE_PATTERN = re.compile(r"ghcr\.io/c2ventures/elecciones2026@sha256:[a-f0-9]{64}")
STAGING_HOST = "preview.xn--eleccionesespaa2026-83b.es"


class DeliveryError(Exception):
    pass


def trusted_run(run: dict, run_id: str) -> None:
    if not (run_id.isdecimal() and str(run.get("id")) == run_id
            and run.get("event") == "push" and run.get("head_branch") == "main"
            and run.get("path") == ".github/workflows/ci.yml"
            and run.get("status") == "completed" and run.get("conclusion") == "success"
            and run.get("repository", {}).get("full_name") == REPOSITORY
            and run.get("head_repository", {}).get("full_name") == REPOSITORY
            and re.fullmatch(r"[a-f0-9]{40}", run.get("head_sha", ""))):
        raise DeliveryError("Only a successful canonical main push CI run is accepted")


def candidate(record: dict, run: dict) -> str:
    image = record.get("image", "")
    if not (record.get("schema") == 1 and IMAGE_PATTERN.fullmatch(image)
            and record.get("revision") == run["head_sha"]
            and record.get("run_id") == str(run["id"])
            and record.get("run_attempt") == str(run["run_attempt"])
            and record.get("platform") == "linux/amd64"
            and record.get("classification") == "private-staging"
            and record.get("election_id") == "es-gen-2023"
            and record.get("quiz_mode") == "unavailable"
            and record.get("pilot_mode") == "source-linked-provisional"
            and record.get("canonical_base") == "https://xn--eleccionesespaa2026-83b.es"
            and re.fullmatch(r"[a-f0-9]{64}", record.get("home_sha256", ""))):
        raise DeliveryError("Candidate evidence does not match the approved CI run")
    return image


def read_run(run_id: str) -> dict:
    if not run_id.isdecimal():
        raise DeliveryError("CI run ID must be numeric")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPOSITORY}/actions/runs/{run_id}",
        headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                 "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        run = json.load(response)
    trusted_run(run, run_id)
    return run


# Never follow an edge redirect that could forward staging credentials elsewhere.
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def edge_probe(credential: str | None, expected_hash: str | None = None) -> None:
    headers = {"User-Agent": "elecciones2026-deployment/1"}
    if credential:
        encoded = base64.b64encode(credential.encode()).decode()
        headers["Authorization"] = f"Basic {encoded}"
    request = urllib.request.Request(f"https://{STAGING_HOST}/", headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=20) as response:
            if credential is None:
                raise DeliveryError("Staging is reachable without authentication")
            body = response.read(2_000_001)
            actual_hash = hashlib.sha256(body).hexdigest()
            checks = {
                "HTTP status": response.status == 200,
                "response size": len(body) <= 2_000_000,
                "no-store": "no-store" in response.headers.get("Cache-Control", ""),
                "CSP": bool(response.headers.get("Content-Security-Policy")),
                "nosniff": response.headers.get("X-Content-Type-Options") == "nosniff",
                "frame protection": response.headers.get("X-Frame-Options") == "DENY",
                "content hash": not expected_hash or actual_hash == expected_hash,
            }
            failures = [name for name, passed in checks.items() if not passed]
            if failures:
                encoding = response.headers.get("Content-Encoding", "identity").lower()
                # Allowlisted metadata only: never echo arbitrary header values,
                # page contents, request credentials or an unchecked reference.
                details = {
                    "response_bytes": len(body), "response_sha256": actual_hash,
                    "expected_sha256": expected_hash if expected_hash and re.fullmatch(r"[a-f0-9]{64}", expected_hash) else None,
                    "content_encoding": encoding if encoding in {"identity", "gzip", "br", "deflate", "zstd"} else "other",
                    "email_obfuscation": b"email-decode.min.js" in body,
                    "rocket_loader": b"rocket-loader.min.js" in body,
                    "analytics_beacon": b"static.cloudflareinsights.com/beacon.min.js" in body,
                    "challenge_script": b"/cdn-cgi/challenge-platform/" in body,
                }
                print("Staging response metadata: " + json.dumps(details), flush=True)
                raise DeliveryError("External staging verification failed: " + ", ".join(failures))
    except urllib.error.HTTPError as exc:
        if credential is None and exc.code == 401:
            exc.close()
            return
        exc.close()
        raise DeliveryError(f"External staging response failed: HTTP {exc.code}") from None


def deliver(image: str, home_hash: str) -> None:
    host, user, port = (os.environ.get(name, "") for name in
                        ("VPS_HOST", "VPS_USER", "VPS_SSH_PORT"))
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", host) or user != "deployer"
            or not port.isdecimal() or not 1 <= int(port) <= 65535):
        raise DeliveryError("Invalid SSH connection settings")
    key, trust, auth = (os.environ.get(name, "") for name in
                        ("VPS_SSH_KEY", "VPS_KNOWN_HOSTS", "STAGING_BASIC_AUTH"))
    if not key.strip() or not trust.strip() or ":" not in auth:
        raise DeliveryError("Missing SSH or staging credentials")
    # Reject an accidentally public staging route before changing the origin.
    print("Checking unauthenticated staging access before deployment.", flush=True)
    edge_probe(None)
    with tempfile.TemporaryDirectory(prefix="elections-ssh-") as directory:
        key_path, trust_path = Path(directory) / "key", Path(directory) / "known_hosts"
        for path, value in ((key_path, key), (trust_path, trust)):
            path.write_text(value.rstrip("\n") + "\n")
            path.chmod(0o600)
        command = ["ssh", "-F", "/dev/null", "-T", "-i", str(key_path), "-p", port,
                   "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
                   "-o", "StrictHostKeyChecking=yes",
                   "-o", f"UserKnownHostsFile={trust_path}",
                   "-o", "ConnectTimeout=15", "-o", "ServerAliveInterval=15",
                   "-o", "ServerAliveCountMax=3", f"{user}@{host}"]
        subprocess.run([*command, "check"], check=True, timeout=30, stdin=subprocess.DEVNULL)
        subprocess.run([*command, f"deploy {image}"], check=True, timeout=300,
                       stdin=subprocess.DEVNULL)
    # Report a failure without automatically rolling back a possible factual correction.
    print("Checking unauthenticated staging access after deployment.", flush=True)
    edge_probe(None)
    print("Checking authenticated staging content and headers.", flush=True)
    edge_probe(auth, home_hash)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()
    try:
        run = read_run(args.run_id)
        if args.candidate:
            record = json.loads(args.candidate.read_text())
            image = candidate(record, run)
            deliver(image, record["home_sha256"])
            summary = os.environ.get("GITHUB_STEP_SUMMARY")
            if summary:
                with open(summary, "a") as output:
                    output.write(f"Authenticated staging verified.\n\nRevision: `{record['revision']}`\n\nImage: `{image}`\n")
        else:
            print("Trusted CI run verified; no deployment performed.")
    except DeliveryError as error:
        # These messages contain only controlled labels/status codes, never raw
        # HTTP bodies, credentials, connection settings or subprocess errors.
        print(f"Delivery blocked: {error}")
        return 1
    except (KeyError, ValueError, OSError, subprocess.SubprocessError):
        print("Delivery failed. Inspect CI evidence and use the protected operator recovery procedure.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
