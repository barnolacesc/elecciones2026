"""Private archive boundaries use synthetic PDFs; CI never downloads party sources."""
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock
import urllib.error

from elecciones2026 import private_archive as archive
from elecciones2026.importer import (
    DisallowedHostError, HashMismatchError, ImportConfig, InvalidFileFormatError,
    SizeLimitExceededError, fetch_url_with_limits, validate_url,
)
from elecciones2026.source_register import load_register

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "sha256:" + "a" * 64


def synthetic_pdf() -> bytes:
    """Valid three-page PDF with a blank middle page and distinct page text."""
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [4 0 R 6 0 R 8 0 R] /Count 3 >>",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for page, text in enumerate(["First physical page", "", "Third physical page"], 1):
        content_id = 3 + page * 2
        objects.append((f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                        f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>").encode())
        content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET\n".encode()
        objects.append(f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"endstream")
    result = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    start = len(result)
    result.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        result.extend(f"{offset:010} 00000 n \n".encode())
    result.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode())
    return bytes(result)


class FakeExtractor:
    image_id = IMAGE
    platform = "linux/test"

    def extract(self, pdf):
        return {"page_count": 3, "pages": ["first\n", "", "third\n"],
                "extractor": "pdftotext version test"}


class PrivateArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "private"
        self.pdf = synthetic_pdf()
        original = next(s for s in load_register(ROOT / "content/sources/register.json").sources
                        if s.id == "src-2023-pp-v1")
        self.source = replace(original, sha256=archive.sha256(self.pdf))

    def store(self):
        return archive.archive_bytes(self.root, self.source, self.pdf, {"method": "synthetic-test"})

    def test_acquisition_checks_hash_and_keeps_source_version_and_dates(self):
        path = self.store()
        metadata = json.loads((path / "retrieval.json").read_bytes())
        self.assertEqual(metadata["source_version"], self.source.version)
        self.assertEqual(metadata["election_id"], "es-gen-2023")
        self.assertEqual(metadata["registered_retrieval_date"], self.source.retrieval_date)
        self.assertIn("+00:00", metadata["acquired_at"])
        self.assertEqual(metadata["editorial_approval"], "not_granted_by_archive")
        self.assertEqual((path / "original.pdf").stat().st_mode & 0o777, 0o600)
        for p in (self.root, path, path.parent, path.parent.parent):
            self.assertEqual(p.stat().st_mode & 0o777, 0o700)
        self.assertEqual(archive.verify_original(self.root, self.source).read_bytes(), self.pdf)
        before = (path / "retrieval.json").read_bytes()
        self.store()
        self.assertEqual((path / "retrieval.json").read_bytes(), before)

    def test_mismatched_hash_leaves_no_object(self):
        with self.assertRaises(HashMismatchError):
            archive.archive_bytes(self.root, self.source, self.pdf + b"changed", {})
        self.assertEqual(list(self.root.iterdir()), [])

    def test_non_pdf_rejected_even_when_hash_matches(self):
        bad = b"<html>not a PDF</html>"
        with self.assertRaises(InvalidFileFormatError):
            archive.archive_bytes(self.root, replace(self.source, sha256=archive.sha256(bad)), bad, {})

    def test_oversize_rejected_without_storing(self):
        with mock.patch.object(archive, "ImportConfig", return_value=ImportConfig(max_size_bytes=20)):
            with self.assertRaises(SizeLimitExceededError):
                self.store()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_offline_local_acquisition_never_uses_network(self):
        local = Path(self.temp.name) / "input.pdf"
        local.write_bytes(self.pdf)
        with mock.patch.object(archive, "fetch_url_with_limits", side_effect=AssertionError("network")):
            path = archive.acquire(self.root, self.source, frozenset({"www.pp.es"}), local)
        self.assertEqual(json.loads((path / "retrieval.json").read_bytes())["acquisition"]["download_date"],
                         "not_asserted")

    def test_online_acquisition_passes_explicit_host_policy(self):
        with mock.patch.object(archive, "fetch_url_with_limits", return_value=(self.pdf, {})) as fetch:
            archive.acquire(self.root, self.source, frozenset({"www.pp.es"}))
        self.assertEqual(fetch.call_args.args[1].allowed_hosts, frozenset({"www.pp.es"}))

    def test_unallowlisted_source_and_redirect_fail_before_connection(self):
        with mock.patch.object(archive, "fetch_url_with_limits") as fetch:
            with self.assertRaises(archive.ArchiveError):
                archive.acquire(self.root, self.source, frozenset({"static.esquerra.cat"}))
            fetch.assert_not_called()
        config = ImportConfig(allowed_hosts=frozenset({"www.pp.es"}))
        with self.assertRaises(DisallowedHostError):
            validate_url("https://unlisted.example/file.pdf", config)
        redirect = urllib.error.HTTPError(self.source.direct_url, 302, "Found",
                                         {"Location": "https://unlisted.example/file.pdf"}, None)
        opener = mock.Mock()
        opener.open.side_effect = redirect
        with mock.patch("elecciones2026.importer.socket.getaddrinfo",
                        return_value=[(2, 1, 6, "", ("8.8.8.8", 443))]), \
             mock.patch("elecciones2026.importer.urllib.request.build_opener", return_value=opener):
            with self.assertRaises(DisallowedHostError):
                fetch_url_with_limits(self.source.direct_url, config)
        self.assertEqual(opener.open.call_count, 1)

    def test_in_git_checkout_and_symlink_to_checkout_rejected(self):
        with self.assertRaises(archive.ArchiveError):
            archive.private_root(ROOT / "build/private-source-test")
        link = Path(self.temp.name) / "linked"
        link.symlink_to(ROOT, target_is_directory=True)
        with self.assertRaises(archive.ArchiveError):
            archive.private_root(link / "build/private-source-test")
        checkout = Path(self.temp.name) / "checkout"
        checkout.mkdir()
        (checkout / ".git").write_text("gitdir: /elsewhere")
        with self.assertRaises(archive.ArchiveError):
            archive.private_root(checkout / "private")

    def test_unsafe_ids_missing_hash_and_nonprivate_storage_rejected(self):
        for source in (replace(self.source, id="../escape"), replace(self.source, sha256=None)):
            with self.assertRaises(archive.ArchiveError):
                archive.archive_bytes(self.root, source, self.pdf, {})
        self.root.chmod(0o755)
        with self.assertRaises(archive.ArchiveError):
            archive.private_root(self.root)

    def test_original_corruption_prevents_extraction(self):
        path = self.store()
        (path / "original.pdf").write_bytes(self.pdf + b"corrupt")
        runner = mock.Mock(wraps=FakeExtractor())
        with self.assertRaises(HashMismatchError):
            archive.extract(self.root, self.source, runner)
        runner.extract.assert_not_called()

    def test_archive_symlink_cannot_escape(self):
        path = self.store()
        (path / "original.pdf").unlink()
        outside = Path(self.temp.name) / "other.pdf"
        outside.write_bytes(self.pdf)
        outside.chmod(0o600)
        (path / "original.pdf").symlink_to(outside)
        with self.assertRaises(archive.ArchiveError):
            archive.verify_original(self.root, self.source)

    def test_hard_links_and_invalid_acquisition_metadata_rejected(self):
        path = self.store()
        os.link(path / "original.pdf", Path(self.temp.name) / "hardlink.pdf")
        with self.assertRaises(archive.ArchiveError):
            archive.verify_original(self.root, self.source)
        (Path(self.temp.name) / "hardlink.pdf").unlink()
        for malformed in (b"[]", b"{invalid", b'{"source_id": "wrong-source"}'):
            (path / "retrieval.json").write_bytes(malformed)
            with self.assertRaises(archive.ArchiveError):
                archive.verify_original(self.root, self.source)

    def test_page_mapping_blank_pages_hashes_and_repeat_determinism(self):
        self.store()
        path = archive.extract(self.root, self.source, FakeExtractor())
        before = {f.name: f.read_bytes() for f in path.iterdir()}
        self.assertEqual(archive.extract(self.root, self.source, FakeExtractor()), path)
        self.assertEqual(before, {f.name: f.read_bytes() for f in path.iterdir()})
        artifact = json.loads(before["pages.json"])
        self.assertEqual([p["pdf_page"] for p in artifact["pages"]], [1, 2, 3])
        self.assertEqual(artifact["pages"][1]["text"], "")
        self.assertEqual(artifact["pages"][1]["text_sha256"], archive.sha256(b""))
        self.assertIn(b'pdf-page-3', before["review.md"])
        self.assertFalse(artifact["authoritative_quote"])
        self.assertEqual(archive.verify_extraction(self.root, self.source, IMAGE), path)

    def test_inconsistent_page_count_and_excessive_text_rejected(self):
        for payload in ({"pages": ["a"], "page_count": 2}, {"pages": ["a\fb"], "page_count": 1}):
            with self.assertRaises(archive.ArchiveError):
                archive.make_artifacts(self.source, payload, IMAGE, "linux/test")
        with mock.patch.object(archive, "MAX_TEXT_BYTES", 2):
            with self.assertRaises(archive.ArchiveError):
                archive.make_artifacts(self.source, FakeExtractor().extract(None), IMAGE, "linux/test")

    def test_changed_extraction_fails_without_overwriting(self):
        self.store()
        path = archive.extract(self.root, self.source, FakeExtractor())
        before = (path / "pages.json").read_bytes()
        runner = FakeExtractor()
        runner.extract = lambda pdf: {"pages": ["changed", "", "third"], "page_count": 3,
                                      "extractor": "pdftotext version test"}
        with self.assertRaises(archive.ArchiveError):
            archive.extract(self.root, self.source, runner)
        self.assertEqual((path / "pages.json").read_bytes(), before)

    def test_tampered_text_or_manifest_rejected(self):
        self.store()
        path = archive.extract(self.root, self.source, FakeExtractor())
        for filename in ("review.md", "manifest.json", "pages.json"):
            original = (path / filename).read_bytes()
            if filename == "manifest.json":
                modified = json.loads(original)
                modified["pages_sha256"] = "0" * 64
                data = archive.canonical_json(modified)
            elif filename == "pages.json":
                modified = json.loads(original)
                modified["pages"][2]["pdf_page"] = 4
                data = archive.canonical_json(modified)
            else:
                data = original + b"tamper"
            (path / filename).write_bytes(data)
            with self.assertRaises(archive.ArchiveError):
                archive.verify_extraction(self.root, self.source, IMAGE)
            (path / filename).write_bytes(original)

    def test_private_files_are_ignored_and_public_build_has_no_archive(self):
        from elecciones2026.generator import build_site
        self.store()
        archive.extract(self.root, self.source, FakeExtractor())
        output = Path(self.temp.name) / "public"
        build_site(ROOT, output, build_date="2026-10-10")
        for filename in ("original.pdf", "pages.json", "review.md", "retrieval.json", "manifest.json"):
            self.assertEqual(list(output.rglob(filename)), [])
        self.assertNotIn(str(self.root), "".join(p.read_text(errors="ignore") for p in output.rglob("*.html")))
        ignore = (ROOT / ".dockerignore").read_text()
        for pattern in ("**/*.pdf", "**/review.md", "**/pages.json"):
            self.assertIn(pattern, ignore)

    def test_docker_command_is_networkless_bounded_and_has_no_host_mounts(self):
        with mock.patch.object(archive.subprocess, "run", return_value=mock.Mock(stdout=json.dumps([
            {"Id": IMAGE, "Os": "linux", "Architecture": "test"}]).encode())):
            runner = archive.DockerExtractor("a-tag")
        command = runner.command("test")
        for flag in ("--network=none", "--read-only", "--cap-drop=ALL", "--memory=512m", "--pids-limit=32",
                     "--security-opt=no-new-privileges", "--pull=never"):
            self.assertIn(flag, command)
        self.assertNotIn("--mount", command)
        self.assertEqual(command[-1], IMAGE)

    def test_public_build_rejects_private_files_before_copying(self):
        from elecciones2026.generator import build_site
        source_root = Path(self.temp.name) / "build-input"
        shutil.copytree(ROOT / "site", source_root / "site")
        shutil.copytree(ROOT / "content", source_root / "content")
        output = Path(self.temp.name) / "public"
        for filename in ("pages.json", "review.md", "source.PDF"):
            misplaced = source_root / "site/tokens" / filename
            misplaced.write_bytes(b"private source sentinel")
            with self.assertRaisesRegex(ValueError, "Private source artifact"):
                build_site(source_root, output, build_date="2026-10-10")
            self.assertFalse(output.exists())
            misplaced.unlink()
        output.mkdir()
        (output / "retrieval.json").write_bytes(b"old private source sentinel")
        with self.assertRaisesRegex(ValueError, "Private source artifact"):
            build_site(source_root, output, build_date="2026-10-10")

    def test_failed_extraction_leaves_no_derivative_bundle(self):
        path = self.store()
        runner = FakeExtractor()
        runner.extract = mock.Mock(side_effect=archive.ArchiveError("Parser rejected document"))
        with self.assertRaises(archive.ArchiveError):
            archive.extract(self.root, self.source, runner)
        self.assertFalse((path / "extractions").exists())


@unittest.skipUnless(os.environ.get("ELECTIONS_TEST_PDF_IMAGE"), "Explicit synthetic Docker integration only")
class DockerPDFIntegrationTests(unittest.TestCase):
    setUp = PrivateArchiveTests.setUp
    store = PrivateArchiveTests.store

    def test_parser_rejects_damaged_pdf_with_no_partial_extraction(self):
        data = b"%PDF-1.4\n%%EOF\n"
        source = replace(self.source, sha256=archive.sha256(data))
        path = archive.archive_bytes(self.root, source, data, {"method": "synthetic-test"})
        runner = archive.DockerExtractor(os.environ["ELECTIONS_TEST_PDF_IMAGE"])
        with self.assertRaises(archive.ArchiveError):
            archive.extract(self.root, source, runner)
        self.assertFalse((path / "extractions").exists())

    def test_real_poppler_page_mapping_repeat_and_timeout_cleanup(self):
        self.store()
        runner = archive.DockerExtractor(os.environ["ELECTIONS_TEST_PDF_IMAGE"])
        path = archive.extract(self.root, self.source, runner)
        artifact = json.loads((path / "pages.json").read_bytes())
        self.assertEqual(artifact["page_count"], 3)
        self.assertIn("First physical page", artifact["pages"][0]["text"])
        self.assertEqual(artifact["pages"][1]["text"].strip(), "")
        self.assertIn("Third physical page", artifact["pages"][2]["text"])
        before = (path / "pages.json").read_bytes()
        archive.extract(self.root, self.source, runner)
        self.assertEqual(before, (path / "pages.json").read_bytes())
        runner.timeout = 0.001
        with mock.patch.object(runner, "command", wraps=runner.command) as command:
            with self.assertRaises(archive.ArchiveError):
                runner.extract(path.parent.parent / "original.pdf")
        container_name = command.call_args.args[0]
        result = archive.subprocess.run(["docker", "ps", "-aq", "--filter", f"name={container_name}"],
                                        capture_output=True, check=True, timeout=15)
        self.assertEqual(result.stdout.strip(), b"")


if __name__ == "__main__":
    unittest.main()
