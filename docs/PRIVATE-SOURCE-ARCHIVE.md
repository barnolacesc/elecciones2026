# Private PDF archive and editorial extraction

Roadmap package **E1.2**, GitHub issue **#43**. This is internal source-processing tooling. It does not grant source authenticity, quotation rights, human review, or permission to publish. Issue #42 owns the 2023 claim and rights audit. The archive does not write the source register, statement records, or editorial approvals.

## Local setup

Use Python 3.14 and Docker on an editor's machine. No paid service or public host is needed. The archive must be outside **every Git checkout**, outside web-serving directories, and owned by the operator with directory mode `0700`. Files have mode `0600`. Resolved symlinks into Git, symlinks within the archive, and hard-linked archive files are rejected. Do not weaken permissions to share files; each authorised editor should have a private copy or use an owner-approved private access mechanism.

From the repository root:

```sh
mkdir -p "$HOME/Library/Application Support/elecciones2026/private-sources"
chmod 700 "$HOME/Library/Application Support/elecciones2026/private-sources"
export ELECTIONS_PRIVATE_ARCHIVE="$HOME/Library/Application Support/elecciones2026/private-sources"
docker build --tag elecciones-private-pdf:local tools/private-pdf
export ELECTIONS_PDF_IMAGE_ID="$(docker image inspect elecciones-private-pdf:local --format '{{.Id}}')"
```

On Linux, an owner-only directory such as `$HOME/.local/share/elecciones2026/private-sources` is suitable. Docker must have permission to run locally. The worker receives the verified PDF on standard input; it has no host filesystem mounts, archive access, Docker socket, or credentials.

The Dockerfile pins the base by digest and Poppler package to `25.12.0-r1`. Its other APK dependencies can change on rebuild; a rebuild is **not** assumed to be byte-identical. Retain the exact local image ID and platform for repeat processing, and save the image with private backups. Extraction never pulls an image. Review package changes and advisories before updating the worker. An unavailable pinned package fails the build; do not silently use an unpinned version.

## Acquire explicitly, then process offline

`content/sources/download-policy.json` lists the exact official hosts permitted for the four registered 2023 rehearsal sources (PP, ERC, PNV and Sumar). Review any additions, including redirects. HTTPS, standard port, DNS/private-address checks, redirect limits, 15-second socket timeouts, permitted MIME types, a 50 MiB ceiling, PDF inspection, and the **registered** SHA-256 apply before storage. Missing hashes are rejected. A changed remote document is not automatically accepted or relabelled.

The four rows in `content/sources/register.json` are a **pilot**, not an approved
2023 candidature or programme denominator. All four remain
`published-unverified`, with rights `not_reviewed` and unknown publication
dates. The dated `docs/pilot-review/2023/inventory.json` reports local byte and
extraction checks for these four originals as of 2026-10-12; that historical
check does not prove current remote bytes, source authenticity, rights or
topic coverage. Reconcile the registered URL, hash and private archive object
before a new acquisition. A remote hash mismatch must stop for source-owner
review; do not change the registered hash merely to make the download pass.

Acquisition is the only document-processing command that can contact an official party host:

```sh
for source in src-2023-pp-v1 src-2023-erc-v1 src-2023-pnv-v1 src-2023-sumar-v1; do
  PYTHONPATH=src python3 -m elecciones2026.private_archive acquire \
    --archive "$ELECTIONS_PRIVATE_ARCHIVE" --source-id "$source"
done
```

For a previously downloaded PDF, add `--file /absolute/private/path/document.pdf` to `acquire`. This route performs no network access and still verifies the registered checksum. It records the time of local import without asserting the original download date. Acquisition records distinguish the source register's retrieval date from the actual archive acquisition timestamp in UTC. Repeat acquisition checks the existing object and retains its first acquisition record.

Once the image and originals are local, extraction and verification need no external network:

```sh
for source in src-2023-pp-v1 src-2023-erc-v1 src-2023-pnv-v1 src-2023-sumar-v1; do
  PYTHONPATH=src python3 -m elecciones2026.private_archive extract \
    --archive "$ELECTIONS_PRIVATE_ARCHIVE" --source-id "$source" \
    --image "$ELECTIONS_PDF_IMAGE_ID"
  PYTHONPATH=src python3 -m elecciones2026.private_archive verify \
    --archive "$ELECTIONS_PRIVATE_ARCHIVE" --source-id "$source" \
    --image "$ELECTIONS_PDF_IMAGE_ID"
done
```

Running `verify` without `--image` checks the original and acquisition metadata only. With `--image`, use the exact `sha256:…` image ID: this check does not require Docker or a network connection.

The worker uses Docker's [container constraints](https://docs.docker.com/engine/containers/run/): no network, no capabilities, no privilege escalation, a non-root user, a read-only root filesystem, 512 MiB memory including swap, one CPU, 32 processes, a 96 MiB temporary filesystem, and a 64 MiB file-size limit. The host enforces a 120-second wall-clock deadline and 64 MiB output limit and removes its own container on success or failure. The worker limits input to 50 MiB, extracted text to 32 MiB, and physical pages to 1,000. It rejects encrypted PDFs, parser failures/diagnostics, invalid UTF-8, and mismatched page delimiters. Static token inspection is an additional filter, not a complete malicious-PDF detector. The isolation depends on a maintained Docker host and trusted worker image.

## Storage and the issue #42 interface

Objects are keyed by immutable election ID, source ID, and the registered PDF checksum:

```text
<private archive>/<election_id>/<source_id>/<source_sha256>/
  original.pdf
  retrieval.json
  extractions/<image_id_without_sha256_prefix>/
    pages.json
    review.md
    manifest.json
```

`retrieval.json` records source ID, election ID, local source-version label, official and direct URLs, source checksum, file size, registered retrieval date, actual acquisition timestamp, acquisition method, and the existing rights-record snapshot. That snapshot is historical metadata, not proof of human approval. The `23J-v1` version label comes from the register; the workflow does not assert that it is a publisher-issued revision identifier.

`pages.json` is the machine-readable editorial interface:

- `source_id`, `election_id`, `source_version`, and `source_sha256` join to the register and the audit record.
- `image_id`, `platform`, `extractor`, and extraction options identify the toolchain.
- Each page has `pdf_page` (1-based physical PDF position), `anchor` (`pdf-page-N`), exact extracted `text`, and `text_sha256` (SHA-256 of that page's UTF-8 bytes).
- Empty physical pages remain in the sequence. `page_count` must match the parser and form-feed boundaries.

`review.md` preserves extracted layout in fenced text and includes the same page anchors. `manifest.json` hashes the complete JSON and Markdown artifacts. No current timestamp enters extraction artifacts. Re-extracting the same original with the same image/platform must produce identical artifacts; a mismatch fails without overwriting earlier evidence. Verification rechecks the original, aggregate checksums, page hashes/anchors, and canonical serialization.

Physical PDF pages and printed page labels can differ. A `source_page` in an editorial statement must be reconciled manually with the physical page and printed label; do not silently equate them. Editors can open the official PDF at `#page=N` for the physical page or inspect `original.pdf` locally. Extraction can reorder columns, miss image-only text, or misread glyphs. Empty text does not prove that a page is empty or that a policy is absent. There is no OCR or AI quotation generation in this workflow. Verify wording, context, printed labels, summaries, and qualifications visually in the original PDF and record two distinct human reviews separately.

## Retention, replacements, access, and backup

The editorial owner must approve the retention period and access list. Until then, this workflow performs no automatic deletion or backup and authorises no further distribution. Keep local copies only for the authorised internal review purpose. Remove abandoned temporary `.acquire-*` or `.extract-*` directories after checking that no processing job is active.

Never overwrite an earlier PDF/version to accept a new hash. Have the source-register/editorial workflow record the replacement, its reason, the new source version/hash, and dependent claim invalidation. Archive the replacement as a separate object, retaining earlier evidence for the approved correction/retention period. If the publisher URL now serves different bytes, acquisition fails; a source owner must resolve it rather than changing the checksum merely to pass the check.

Restrict originals, full text, backups, and saved worker images to authorised editors. Do not upload them to Git, CI artifacts, public preview directories, or general-purpose external tools. Use an owner-approved encrypted local/offline backup destination outside Git, and include the whole object directory plus the exact worker image (`docker image save`). Protect the backup's access and encryption keys separately. On restore, recreate owner-only permissions and run `verify` for each original and extraction; confirm the restored image ID before re-extracting. A tested encrypted backup and an approved retention schedule remain owner responsibilities; neither is presumed by the local rehearsal.

`.gitignore` and `.dockerignore` exclude source PDFs and full extraction filenames as defence in depth. The static generator never reads this archive, and the public serving image contains no archive or parser. Public pages continue to link to official sources. A private extraction artifact cannot grant full-text distribution rights or bypass an editorial release gate.

## Verification and CI

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p test_private_archive.py -v
PYTHONPATH=src ELECTIONS_TEST_PDF_IMAGE="$ELECTIONS_PDF_IMAGE_ID" \
  python3 -m unittest discover -s tests -p test_private_archive.py -v
```

Normal tests use synthetic byte streams and mocked acquisition; the opt-in Docker test uses a generated three-page PDF with a blank middle page. CI builds the worker and runs only synthetic documents. It does not acquire political documents or retain full source artifacts. The documented pilot acquisition commands are explicit local actions, not CI steps.
