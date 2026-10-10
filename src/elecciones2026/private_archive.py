"""Private source acquisition and deterministic offline extraction (E1.2, issue #43).

No archive path or full source text enters the static generator. Acquisition is
explicit; extraction runs only in a networkless, resource-limited container.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import subprocess
import sys
import tempfile
import time
import uuid
from urllib.parse import urlsplit

from elecciones2026.importer import (
    ImportConfig, SourceImportError, fetch_url_with_limits,
    import_source_from_bytes, import_source_from_file, validate_sha256_format,
)
from elecciones2026.source_register import SourceRecord, load_register

REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAT_VERSION = "1.0.0"
MAX_TEXT_BYTES = 32 * 1024 * 1024
MAX_OUTPUT_BYTES = 64 * 1024 * 1024
MAX_PAGES = 1000
IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IMAGE_ID = re.compile(r"^sha256:[a-f0-9]{64}$")


class ArchiveError(SourceImportError):
    """An acquisition, storage, or extraction integrity boundary failed."""


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_root(path: Path) -> Path:
    """Require external, owner-only storage, including for Git linked worktrees."""
    path = path.expanduser().resolve()
    if path == REPO_ROOT or path in REPO_ROOT.parents:
        raise ArchiveError("Archive must not contain the repository")
    if any((parent / ".git").exists() for parent in (path, *path.parents)):
        raise ArchiveError("Archive must be outside every Git checkout")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not path.is_dir() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
        raise ArchiveError("Archive directory must be owned by you with mode 0700")
    return path


def safe_path(root: Path, *parts: str) -> Path:
    path = root.joinpath(*parts)
    cursor = root
    for part in path.relative_to(root).parts:
        cursor /= part
        if cursor.is_symlink():
            raise ArchiveError("Symlinks are forbidden inside the archive")
    if not path.resolve().is_relative_to(root):
        raise ArchiveError("Path escapes private storage")
    return path


def source_key(source: SourceRecord) -> str:
    for value in (source.id, source.election_id):
        if not IDENTIFIER.fullmatch(value):
            raise ArchiveError("Unsafe source or election identifier")
    if not source.version or not source.direct_url or not source.sha256:
        raise ArchiveError("Registered source version, direct URL and SHA-256 are required")
    return validate_sha256_format(source.sha256)


def object_path(root: Path, source: SourceRecord) -> Path:
    return safe_path(root, source.election_id, source.id, source_key(source))


def read_private(path: Path, limit: int) -> bytes:
    if not path.is_file() or path.is_symlink() or path.stat().st_mode & 0o077:
        raise ArchiveError("Expected an owner-only regular archive file")
    if path.stat().st_uid != os.getuid() or path.stat().st_nlink != 1:
        raise ArchiveError("Archive files must be owned by you and have no hard links")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ArchiveError("Archive file exceeds size limit")
    return data


def write_private(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        os.chmod(path, 0o600)
        stream.write(data)


def read_object(path: Path, limit: int) -> dict:
    try:
        value = json.loads(read_private(path, limit))
    except (ValueError, UnicodeError) as error:
        raise ArchiveError("Invalid archive JSON") from error
    if not isinstance(value, dict):
        raise ArchiveError("Archive JSON must be an object")
    return value


def verify_original(root: Path, source: SourceRecord) -> Path:
    root = private_root(root)
    directory = object_path(root, source)
    pdf = safe_path(root, str(directory.relative_to(root)), "original.pdf")
    data = read_private(pdf, ImportConfig().max_size_bytes)
    import_source_from_bytes(data, expected_hash=source.sha256, source_id=source.id,
                             config=ImportConfig(offline_only=True))
    meta = read_object(safe_path(root, str(directory.relative_to(root)), "retrieval.json"), 65536)
    expected = {"source_id": source.id, "election_id": source.election_id,
                "source_version": source.version, "source_sha256": source.sha256,
                "source_url": source.direct_url, "size_bytes": len(data), "format_version": FORMAT_VERSION}
    if any(meta.get(key) != value for key, value in expected.items()):
        raise ArchiveError("Acquisition manifest does not match the registered source")
    return pdf


def archive_bytes(root: Path, source: SourceRecord, data: bytes, acquisition: dict) -> Path:
    root = private_root(root)
    directory = object_path(root, source)
    import_source_from_bytes(data, expected_hash=source.sha256, source_id=source.id,
                             config=ImportConfig(offline_only=True))
    if directory.exists():
        verify_original(root, source)
        return directory
    directory.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    # mkdir(parents=True) uses default permissions for intermediate directories.
    for parent in (directory.parent, directory.parent.parent):
        os.chmod(parent, 0o700)
    metadata = {
        "format_version": FORMAT_VERSION, "source_id": source.id,
        "election_id": source.election_id, "source_version": source.version,
        "source_sha256": source.sha256, "size_bytes": len(data),
        "source_url": source.direct_url, "official_url": source.official_url,
        "registered_retrieval_date": source.retrieval_date,
        "acquired_at": datetime.now(timezone.utc).isoformat(),
        "acquisition": acquisition, "rights_review_snapshot": asdict(source.rights_review),
        "editorial_approval": "not_granted_by_archive",
    }
    with tempfile.TemporaryDirectory(prefix=".acquire-", dir=root) as temp:
        stage = Path(temp) / "object"
        stage.mkdir(mode=0o700)
        write_private(stage / "original.pdf", data)
        write_private(stage / "retrieval.json", canonical_json(metadata))
        stage.rename(directory)
    return directory


def load_policy(path: Path) -> frozenset[str]:
    policy = json.loads(path.read_text(encoding="utf-8"))
    hosts = policy.get("allowed_hosts")
    if not isinstance(hosts, list) or not hosts or any(
        not isinstance(host, str) or not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", host)
        for host in hosts
    ):
        raise ArchiveError("Policy must list explicit lowercase hostnames")
    return frozenset(hosts)


def acquire(root: Path, source: SourceRecord, hosts: frozenset[str], local_file: Path | None = None) -> Path:
    root = private_root(root)
    source_key(source)
    parsed = urlsplit(source.direct_url)
    if parsed.scheme != "https" or parsed.hostname not in hosts or parsed.username or parsed.password:
        raise ArchiveError("Registered PDF URL is not an allowlisted HTTPS source")
    if parsed.port not in (None, 443) or parsed.fragment:
        raise ArchiveError("Nonstandard ports and URL fragments are prohibited")
    if local_file is not None:
        import_source_from_file(local_file, expected_hash=source.sha256,
                                config=ImportConfig(offline_only=True))
        with local_file.open("rb") as stream:
            data = stream.read(ImportConfig().max_size_bytes + 1)
        metadata = {"method": "local-file", "download_date": "not_asserted"}
    else:
        data, metadata = fetch_url_with_limits(source.direct_url, ImportConfig(allowed_hosts=hosts))
        metadata["method"] = "https"
    return archive_bytes(root, source, data, metadata)


class DockerExtractor:
    """Execute a pinned worker without any host mounts or network access."""

    def __init__(self, image: str, timeout: float = 120):
        result = subprocess.run(["docker", "image", "inspect", image], capture_output=True,
                                check=True, timeout=15)
        description = json.loads(result.stdout)[0]
        self.image_id = description["Id"]
        if not IMAGE_ID.fullmatch(self.image_id):
            raise ArchiveError("Docker image must resolve to an immutable image ID")
        self.platform = description["Os"] + "/" + description["Architecture"]
        self.timeout = timeout

    def command(self, name: str) -> list[str]:
        return ["docker", "run", "--rm", "--pull=never", "--name", name,
                "--network=none", "--read-only", "--user=65534:65534",
                "--cap-drop=ALL", "--security-opt=no-new-privileges",
                "--memory=512m", "--memory-swap=512m", "--cpus=1", "--pids-limit=32",
                "--ulimit", "fsize=67108864:67108864", "--ulimit", "nofile=64:64",
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=96m,mode=1777", "-i", self.image_id]

    def extract(self, pdf: Path) -> dict:
        name = "elections-pdf-" + uuid.uuid4().hex
        output = bytearray()
        try:
            with pdf.open("rb") as stream:
                process = subprocess.Popen(self.command(name), stdin=stream,
                                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                try:
                    with selectors.DefaultSelector() as selector:
                        selector.register(process.stdout, selectors.EVENT_READ)
                        deadline = time.monotonic() + self.timeout
                        while True:
                            remaining = deadline - time.monotonic()
                            if remaining <= 0:
                                raise ArchiveError("PDF extraction timed out")
                            if not selector.select(min(remaining, 0.2)):
                                continue
                            chunk = os.read(process.stdout.fileno(), 65536)
                            if not chunk:
                                break
                            output.extend(chunk)
                            if len(output) > MAX_OUTPUT_BYTES:
                                raise ArchiveError("PDF worker output exceeds limit")
                    if process.wait(timeout=max(0.01, deadline - time.monotonic())) != 0:
                        raise ArchiveError("PDF worker rejected document; archive remains unchanged")
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.wait()
                    process.stdout.close()
        finally:
            # Killing the Docker client does not guarantee container termination.
            subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=15, check=False)
        try:
            payload = json.loads(output)
            if not isinstance(payload, dict):
                raise ArchiveError("PDF worker output must be an object")
            return payload
        except (ValueError, UnicodeError) as error:
            raise ArchiveError("Invalid PDF worker output") from error


def make_artifacts(source: SourceRecord, payload: dict, image_id: str, platform: str) -> tuple[bytes, bytes]:
    pages = payload.get("pages")
    if (not isinstance(pages, list) or not 0 < len(pages) <= MAX_PAGES
            or type(payload.get("page_count")) is not int or payload["page_count"] != len(pages)):
        raise ArchiveError("Extracted page mapping is inconsistent")
    if any(not isinstance(text, str) or "\f" in text for text in pages):
        raise ArchiveError("Invalid page text")
    if sum(len(text.encode("utf-8")) for text in pages) > MAX_TEXT_BYTES:
        raise ArchiveError("Extracted text exceeds limit")
    if not isinstance(payload.get("extractor"), str) or not payload["extractor"].startswith("pdftotext version "):
        raise ArchiveError("Missing Poppler version")
    records = [{"pdf_page": i, "anchor": f"pdf-page-{i}", "text": text,
                "text_sha256": sha256(text.encode("utf-8"))} for i, text in enumerate(pages, 1)]
    artifact = {"format_version": FORMAT_VERSION, "source_id": source.id,
                "election_id": source.election_id, "source_version": source.version,
                "source_sha256": source.sha256, "page_count": len(records), "pages": records,
                "extractor": payload["extractor"], "image_id": image_id, "platform": platform,
                "options": ["-layout", "-enc", "UTF-8", "-eol", "unix"],
                "purpose": "internal_editorial_review", "authoritative_quote": False}
    # Plain fenced text preserves whitespace; choose a fence absent from source.
    longest = max((len(match[0]) for text in pages for match in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    markdown = ["# Private editorial extraction\n\n",
                "Internal use only. Verify quotations and printed page labels against original.pdf.\n",
                "PDF page numbers below are 1-based physical pages, not printed labels.\n",
                f"Source: {source.id}; election: {source.election_id}; version: {source.version}\n",
                f"PDF SHA-256: {source.sha256}\n"]
    for page in records:
        markdown.append(f'\n<a id="{page["anchor"]}"></a>\n## PDF page {page["pdf_page"]}\n\n'
                        f'{fence}text\n{page["text"]}' + ("" if page["text"].endswith("\n") else "\n") + f"{fence}\n")
    return canonical_json(artifact), "".join(markdown).encode("utf-8")


def verify_extraction(root: Path, source: SourceRecord, image_id: str) -> Path:
    root = private_root(root)
    if not IMAGE_ID.fullmatch(image_id):
        raise ArchiveError("Invalid image ID")
    pdf = verify_original(root, source)
    directory = safe_path(root, str(pdf.parent.relative_to(root)), "extractions", image_id[7:])
    manifest = read_object(safe_path(root, str(directory.relative_to(root)), "manifest.json"), 65536)
    pages = read_private(safe_path(root, str(directory.relative_to(root)), "pages.json"), MAX_OUTPUT_BYTES)
    markdown = read_private(safe_path(root, str(directory.relative_to(root)), "review.md"), MAX_OUTPUT_BYTES)
    try:
        artifact = json.loads(pages)
        rebuilt = make_artifacts(source, {"pages": [p["text"] for p in artifact["pages"]],
                                          "page_count": artifact["page_count"], "extractor": artifact["extractor"]},
                                 image_id, artifact["platform"])
    except (ValueError, TypeError, KeyError) as error:
        raise ArchiveError("Invalid extraction page records") from error
    expected = {"format_version": FORMAT_VERSION, "image_id": image_id,
                "source_sha256": source.sha256, "pages_sha256": sha256(pages),
                "markdown_sha256": sha256(markdown)}
    if manifest != expected or rebuilt != (pages, markdown):
        raise ArchiveError("Extraction checksum or page mapping mismatch")
    return directory


def extract(root: Path, source: SourceRecord, runner: DockerExtractor) -> Path:
    root = private_root(root)
    pdf = verify_original(root, source)
    pages, markdown = make_artifacts(source, runner.extract(pdf), runner.image_id, runner.platform)
    # Recheck input after parsing, before committing derivative evidence.
    verify_original(root, source)
    directory = safe_path(root, str(pdf.parent.relative_to(root)), "extractions", runner.image_id[7:])
    if directory.exists():
        verify_extraction(root, source, runner.image_id)
        if read_private(directory / "pages.json", MAX_OUTPUT_BYTES) != pages:
            raise ArchiveError("Same image and PDF produced different text; do not overwrite evidence")
        return directory
    directory.parent.mkdir(mode=0o700, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".extract-", dir=root) as temp:
        stage = Path(temp) / "extraction"
        stage.mkdir(mode=0o700)
        write_private(stage / "pages.json", pages)
        write_private(stage / "review.md", markdown)
        write_private(stage / "manifest.json", canonical_json({
            "format_version": FORMAT_VERSION, "image_id": runner.image_id,
            "source_sha256": source.sha256, "pages_sha256": sha256(pages),
            "markdown_sha256": sha256(markdown),
        }))
        stage.rename(directory)
    verify_extraction(root, source, runner.image_id)
    return directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Private source archive; never grants editorial approval")
    parser.add_argument("command", choices=["acquire", "extract", "verify"])
    parser.add_argument("--archive", type=Path, required=True, help="Owner-only directory outside Git")
    parser.add_argument("--register", type=Path, default=REPO_ROOT / "content/sources/register.json")
    parser.add_argument("--policy", type=Path, default=REPO_ROOT / "content/sources/download-policy.json")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--file", type=Path, help="Acquire a previously downloaded PDF offline")
    parser.add_argument("--image", help="Locally built extraction image (resolved to an immutable ID)")
    args = parser.parse_args()
    try:
        sources = [s for s in load_register(args.register).sources if s.id == args.source_id]
        if len(sources) != 1:
            raise ArchiveError("Source ID must select exactly one registered source")
        source = sources[0]
        root = private_root(args.archive)
        if args.command == "acquire":
            if args.image:
                raise ArchiveError("--image is only for extract or verify")
            path = acquire(root, source, load_policy(args.policy), args.file)
        else:
            if args.file:
                raise ArchiveError("--file is only for acquire")
            if args.command == "extract":
                if not args.image:
                    raise ArchiveError("extract requires --image")
                path = extract(root, source, DockerExtractor(args.image))
            elif args.image:
                path = verify_extraction(root, source, args.image)
            else:
                path = verify_original(root, source)
        print(f"OK: {source.id} | {source.sha256} | {path}")
    except (SourceImportError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(f"FAILED: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
