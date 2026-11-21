"""E1.4-2026: Bounded offline private draft-to-production-format staging utility.

Converts private canonical review drafts into schema-shaped draft statement records
without fabricating human approvals, inventing source URLs/versions, or publishing raw source quotes.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any, Optional
from urllib.parse import urlsplit

from elecciones2026.methodology import CORE_TOPIC_IDS
from elecciones2026.schemas import StatementRecord

KEBAB_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class CorpusStagingError(Exception):
    """Base exception for corpus staging errors."""


class OutputPathError(CorpusStagingError):
    """Raised when an output directory violates containment rules (e.g. inside repo or already exists)."""


class HashVerificationError(CorpusStagingError):
    """Raised when frozen source, points, or coverage SHA-256 hashes do not match."""


class InputValidationError(CorpusStagingError):
    """Raised when input run artifacts are missing, malformed, or inconsistent."""


@dataclass(frozen=True)
class SourceVerificationInfo:
    party_id: str
    source_id: str
    source_sha256: str
    points_count: int
    points_sha256: str
    coverage_sha256: str
    directory: Path
    source_url: str
    source_version: str
    programme_id: str
    original_archive_audit_verified: bool


@dataclass(frozen=True)
class StagingResult:
    run_dir: Path
    output_dir: Path
    source_count: int
    statement_count: int
    evidence_count: int
    new_domain_count: int
    existing_domain_new_subtopic_count: int
    manifest_path: Path
    status_path: Path
    original_archive_audit_verified: bool
    human_approval_granted: bool = False


def find_repo_root(start: Optional[Path] = None) -> Optional[Path]:
    """Find the root of the repository by looking for ROADMAP.md or .git."""
    curr = (start or Path(__file__)).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "ROADMAP.md").is_file() and (parent / "openspec").is_dir():
            return parent
        if (parent / ".git").exists():
            return parent
    return None


def assert_output_dir_outside_repo(output_dir: Path, repo_root: Optional[Path] = None) -> Path:
    """Ensure output directory is strictly outside both the actual repository and any specified root."""
    out_resolved = Path(output_dir).resolve()

    # Always check actual repo root regardless of overrides
    actual_root = find_repo_root()
    if actual_root is not None:
        act_resolved = actual_root.resolve()
        if out_resolved == act_resolved or act_resolved in out_resolved.parents:
            raise OutputPathError(
                f"Refusing output directory inside actual repository: '{out_resolved}' is inside '{act_resolved}'."
            )

    # Also check repo_root parameter if explicitly passed
    if repo_root is not None:
        root_resolved = Path(repo_root).resolve()
        if out_resolved == root_resolved or root_resolved in out_resolved.parents:
            raise OutputPathError(
                f"Refusing output directory inside repository root: '{out_resolved}' is inside '{root_resolved}'."
            )

    return out_resolved


def format_source_page(pages: Any) -> Optional[str]:
    """Format exact source page coordinates, rejecting invalid/bool/duplicate/unsorted/non-positive pages.

    Retains exact coordinates:
      [1] -> "1"
      [1, 2, 3] -> "1-3"
      [1, 3, 5] -> "1, 3, 5"
      [1, 2, 4, 5, 7] -> "1-2, 4-5, 7"
    """
    if pages is None:
        return None
    if isinstance(pages, bool):
        raise InputValidationError("Page coordinate cannot be a boolean.")
    if isinstance(pages, int):
        if pages <= 0:
            raise InputValidationError(f"Page coordinate must be positive: {pages}")
        return str(pages)
    if not isinstance(pages, list):
        raise InputValidationError(f"Invalid page coordinates type: {type(pages)}")
    if len(pages) == 0:
        return None

    last_val = 0
    for p in pages:
        if isinstance(p, bool) or not isinstance(p, int):
            raise InputValidationError(f"Invalid page number (must be integer, not bool): {p}")
        if p <= 0:
            raise InputValidationError(f"Page number must be positive: {p}")
        if p <= last_val:
            if p == last_val:
                raise InputValidationError(f"Duplicate page number detected: {p}")
            raise InputValidationError(f"Page numbers must be strictly sorted: {pages}")
        last_val = p

    # Group contiguous ranges
    ranges: list[tuple[int, int]] = []
    start = pages[0]
    prev = pages[0]
    for p in pages[1:]:
        if p == prev + 1:
            prev = p
        else:
            ranges.append((start, prev))
            start = p
            prev = p
    ranges.append((start, prev))

    parts: list[str] = []
    for s, e in ranges:
        if s == e:
            parts.append(str(s))
        else:
            parts.append(f"{s}-{e}")
    return ", ".join(parts)


def validate_point_id(point_id: str) -> None:
    """Validate point ID strictly as a lowercase kebab-case slug."""
    if not isinstance(point_id, str) or not KEBAB_SLUG_PATTERN.match(point_id):
        raise InputValidationError(
            f"Point ID '{point_id}' must be a valid lowercase kebab-case slug; lossy sanitization is forbidden."
        )


def verify_taxonomy_proposal(run_dir: Path) -> Optional[dict[str, set[str]]]:
    """Verify proposed taxonomy against coordinator validation hashes if available.

    Returns mapping of topic_id -> set of subtopic_ids.
    """
    coord_file = run_dir / "taxonomy-coordinator-validation.json"
    if not coord_file.is_file():
        return None

    coord_data = json.loads(coord_file.read_text(encoding="utf-8"))
    expected_tax_hash = coord_data.get("taxonomy_file_sha256")
    expected_map_hash = coord_data.get("mappings_file_sha256")

    tax_file = run_dir / "taxonomy-review" / "proposed-taxonomy.json"
    map_file = run_dir / "taxonomy-review" / "mappings.json"

    if expected_tax_hash:
        if not tax_file.is_file():
            raise InputValidationError(f"Missing proposed-taxonomy.json required by coordinator validation: {tax_file}")
        actual_tax_hash = hashlib.sha256(tax_file.read_bytes()).hexdigest()
        if actual_tax_hash != expected_tax_hash:
            raise HashVerificationError(
                f"Proposed taxonomy file hash mismatch: expected {expected_tax_hash}, computed {actual_tax_hash}"
            )

    if expected_map_hash:
        if not map_file.is_file():
            raise InputValidationError(f"Missing mappings.json required by coordinator validation: {map_file}")
        actual_map_hash = hashlib.sha256(map_file.read_bytes()).hexdigest()
        if actual_map_hash != expected_map_hash:
            raise HashVerificationError(
                f"Mappings file hash mismatch: expected {expected_map_hash}, computed {actual_map_hash}"
            )

    if tax_file.is_file():
        tax_data = json.loads(tax_file.read_text(encoding="utf-8"))
        topics_map: dict[str, set[str]] = {}
        for t in tax_data.get("topics", []):
            tid = t.get("id")
            if tid:
                subtopics = {s.get("id") for s in t.get("subtopics", []) if s.get("id")}
                topics_map[tid] = subtopics
        return topics_map

    return None


def verify_original_archive_audit(run_dir: Path, expected_sources: dict[str, str]) -> bool:
    """Check a prior archive integrity audit; this does not rehash original bytes."""
    audit_file = run_dir / "source-integrity-audit.json"
    if not audit_file.is_file():
        return False

    audit_data = json.loads(audit_file.read_text(encoding="utf-8"))
    audit_map = {item.get("source_id"): item for item in audit_data if item.get("source_id")}

    for source_id, expected_hash in expected_sources.items():
        entry = audit_map.get(source_id)
        if not entry:
            raise HashVerificationError(f"Source '{source_id}' missing from source-integrity-audit.json")
        if entry.get("original_sha256") != expected_hash:
            raise HashVerificationError(
                f"Original archive SHA-256 mismatch for source '{source_id}': expected {expected_hash}, got {entry.get('original_sha256')}"
            )
        if not entry.get("original_unchanged"):
            raise HashVerificationError(f"Original archive marked changed for source '{source_id}' in audit")
        if not entry.get("page_hashes_verified"):
            raise HashVerificationError(f"Page hashes not verified for source '{source_id}' in audit")

    return True


def verify_and_resolve_sources(
    run_dir: Path,
    manifest: dict[str, Any],
    summary: dict[str, Any],
    jobs: Optional[list[dict[str, Any]]] = None,
) -> tuple[list[SourceVerificationInfo], bool]:
    """Verify frozen hashes for sources, points, and coverage ledgers without invented URLs or versions."""
    canonical_sources = summary.get("canonical_sources", {})
    manifest_sources = manifest.get("sources", [])

    if not jobs:
        raise InputValidationError("jobs.json is required to resolve exact, verified source URLs and versions.")

    jobs_map: dict[str, dict[str, Any]] = {}
    for job in jobs:
        sid = job.get("source_id")
        pid = job.get("party_id")
        if sid:
            jobs_map[sid] = job
        if pid:
            jobs_map[pid] = job

    expected_source_hashes = {entry["source_id"]: entry["source_sha256"] for entry in manifest_sources}
    archive_audit_verified = verify_original_archive_audit(run_dir, expected_source_hashes)

    verified: list[SourceVerificationInfo] = []

    for entry in manifest_sources:
        party_id = entry["party_id"]
        source_id = entry["source_id"]
        expected_src_hash = entry["source_sha256"]
        expected_pts_hash = entry["points_sha256"]
        expected_cov_hash = entry["coverage_sha256"]
        expected_count = entry["points_count"]

        canon_info = canonical_sources.get(party_id)
        if not canon_info:
            raise InputValidationError(f"Party '{party_id}' present in manifest but missing from canonical_sources.")

        raw_dir = canon_info.get("directory", "")
        candidate_dir = run_dir / Path(raw_dir).name
        if candidate_dir.is_dir():
            canon_dir = candidate_dir
        elif Path(raw_dir).is_dir():
            canon_dir = Path(raw_dir)
        else:
            raise InputValidationError(f"Canonical directory for party '{party_id}' does not exist: {raw_dir}")

        pts_file = canon_dir / "points.json"
        cov_file = canon_dir / "page-coverage.json"

        if not pts_file.is_file():
            raise InputValidationError(f"Missing points.json for party '{party_id}' in {canon_dir}")
        if not cov_file.is_file():
            raise InputValidationError(f"Missing page-coverage.json for party '{party_id}' in {canon_dir}")

        actual_pts_bytes = pts_file.read_bytes()
        actual_pts_hash = hashlib.sha256(actual_pts_bytes).hexdigest()
        if actual_pts_hash != expected_pts_hash:
            raise HashVerificationError(
                f"Frozen points hash mismatch for party '{party_id}': expected {expected_pts_hash}, computed {actual_pts_hash}."
            )

        actual_cov_bytes = cov_file.read_bytes()
        actual_cov_hash = hashlib.sha256(actual_cov_bytes).hexdigest()
        if actual_cov_hash != expected_cov_hash:
            raise HashVerificationError(
                f"Frozen coverage hash mismatch for party '{party_id}': expected {expected_cov_hash}, computed {actual_cov_hash}."
            )

        pts_data = json.loads(actual_pts_bytes.decode("utf-8"))
        if (pts_data.get("source_id") != source_id
                or pts_data.get("election_id") != manifest.get("election_id")):
            raise InputValidationError(f"Canonical source/election mismatch: {source_id}")
        coverage_data = json.loads(actual_cov_bytes)
        if coverage_data.get("source_id") != source_id:
            raise InputValidationError(f"Coverage source mismatch: {source_id}")
        actual_src_hash = pts_data.get("source_sha256")
        if actual_src_hash != expected_src_hash:
            raise HashVerificationError(
                f"Frozen source hash mismatch for party '{party_id}': expected {expected_src_hash}, found in points.json {actual_src_hash}."
            )

        points_list = pts_data.get("points", [])
        if len(points_list) != expected_count:
            raise InputValidationError(
                f"Point count mismatch for party '{party_id}': manifest expected {expected_count}, points.json contains {len(points_list)}."
            )

        # Retrieve exact source_url and source_version from jobs
        job_info = jobs_map.get(source_id) or jobs_map.get(party_id)
        if not job_info:
            raise InputValidationError(f"Party '{party_id}' ({source_id}) missing from jobs.json.")

        job_src_hash = job_info.get("source_sha256")
        if job_src_hash and job_src_hash != expected_src_hash:
            raise HashVerificationError(
                f"Source hash mismatch in jobs.json for party '{party_id}': expected {expected_src_hash}, got {job_src_hash}"
            )

        source_url = job_info.get("source_url")
        url = urlsplit(source_url) if isinstance(source_url, str) else None
        if (not url or url.scheme != "https" or not url.hostname
                or url.username is not None or url.password is not None or url.fragment):
            raise InputValidationError(
                f"Exact HTTPS source_url required for party '{party_id}' ({source_id}); missing or invalid URL '{source_url}'."
            )

        source_version = job_info.get("source_version")
        if not source_version or not isinstance(source_version, str) or not source_version.strip():
            raise InputValidationError(
                f"Exact source_version required for party '{party_id}' ({source_id}); missing or empty version."
            )
        if pts_data.get("source_version") != source_version:
            raise InputValidationError(f"Canonical source version mismatch: {source_id}")

        # Conventional draft programme_id mapping
        programme_id = f"prog-{source_id[4:]}" if source_id.startswith("src-") else f"prog-{source_id}"

        verified.append(
            SourceVerificationInfo(
                party_id=party_id,
                source_id=source_id,
                source_sha256=expected_src_hash,
                points_count=expected_count,
                points_sha256=expected_pts_hash,
                coverage_sha256=expected_cov_hash,
                directory=canon_dir,
                source_url=source_url,
                source_version=source_version,
                programme_id=programme_id,
                original_archive_audit_verified=archive_audit_verified,
            )
        )

    return verified, archive_audit_verified


def stage_corpus(
    run_dir: Path | str,
    output_dir: Path | str,
    repo_root: Optional[Path | str] = None,
) -> StagingResult:
    """Stage private draft corpus into schema-shaped production records."""
    run_path = Path(run_dir).resolve()
    out_path = Path(output_dir).resolve()

    # 1. Output directory safety checks
    assert_output_dir_outside_repo(out_path, repo_root)
    if out_path.exists():
        raise OutputPathError(
            f"Output directory '{out_path}' already exists; refuse overwriting existing output "
            f"so stale, mixed, or partial publication sets cannot be mistaken as complete."
        )

    # 2. Input file presence checks
    manifest_file = run_path / "canonical-draft-manifest.json"
    summary_file = run_path / "corpus-summary.json"
    proposed_file = run_path / "proposed-classification-index.json"
    jobs_file = run_path / "jobs.json"

    if not manifest_file.is_file():
        raise InputValidationError(f"Missing canonical-draft-manifest.json in {run_path}")
    if not summary_file.is_file():
        raise InputValidationError(f"Missing corpus-summary.json in {run_path}")
    if not proposed_file.is_file():
        raise InputValidationError(f"Missing proposed-classification-index.json in {run_path}")
    if not jobs_file.is_file():
        raise InputValidationError(f"Missing jobs.json in {run_path}")

    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
    summary_data = json.loads(summary_file.read_text(encoding="utf-8"))
    proposed_data = json.loads(proposed_file.read_text(encoding="utf-8"))
    jobs_data = json.loads(jobs_file.read_text(encoding="utf-8"))

    # 3. Verify sources and frozen hashes
    verified_sources, archive_audit_verified = verify_and_resolve_sources(
        run_path, manifest_data, summary_data, jobs_data
    )

    # 4. Verify taxonomy coordinator validation if present
    proposed_taxonomy_topics = verify_taxonomy_proposal(run_path)
    frozen_mappings = {}
    if (run_path / "taxonomy-coordinator-validation.json").is_file():
        for row in json.loads((run_path / "taxonomy-review/mappings.json").read_text()):
            if row["point_id"] in frozen_mappings:
                raise InputValidationError("Duplicate point in frozen taxonomy mappings")
            frozen_mappings[row["point_id"]] = row

    # 5. Verify proposed classification index integrity
    proposed_points = proposed_data.get("points", [])
    proposed_map: dict[str, dict[str, Any]] = {}
    for p in proposed_points:
        pid = p.get("point_id")
        if not pid:
            raise InputValidationError("Encountered row in proposed-classification-index without point_id")
        if pid in proposed_map:
            raise InputValidationError(f"Duplicate point_id '{pid}' in proposed-classification-index.json")
        proposed_map[pid] = p

    # 6. Pre-validation of all points in-memory before disk writes
    in_memory_records: list[dict[str, Any]] = []
    seen_statement_ids: set[str] = set()
    total_canonical_points = 0
    new_domain_count = 0
    existing_domain_new_subtopic_count = 0

    for src_info in verified_sources:
        pts_file = src_info.directory / "points.json"
        pts_content = json.loads(pts_file.read_text(encoding="utf-8"))
        election_id = pts_content.get("election_id", manifest_data.get("election_id", "es-gen-2026"))

        for pt in pts_content.get("points", []):
            pt_id = pt.get("id")
            if not pt_id:
                raise InputValidationError("Encountered point without id")
            validate_point_id(pt_id)

            if pt_id in seen_statement_ids:
                raise InputValidationError(f"Duplicate point ID encountered: '{pt_id}'")
            seen_statement_ids.add(pt_id)
            total_canonical_points += 1

            prop = proposed_map.get(pt_id)
            if not prop:
                raise InputValidationError(f"Canonical point '{pt_id}' missing from proposed-classification-index.json")

            # Check party_id binding
            if prop.get("party_id") != src_info.party_id:
                raise InputValidationError(
                    f"Party ID mismatch for point '{pt_id}': canonical '{src_info.party_id}', proposed '{prop.get('party_id')}'"
                )

            topic_id = prop.get("topic_id")
            subtopic_id = prop.get("subtopic_id")
            if not topic_id or not subtopic_id:
                raise InputValidationError(f"Point '{pt_id}' lacks proposed topic_id or subtopic_id")

            mapping = frozen_mappings.get(pt_id)
            if mapping:
                if (mapping.get("party_id"), mapping.get("source_id")) != (src_info.party_id, src_info.source_id):
                    raise InputValidationError(f"Frozen mapping source mismatch: {pt_id}")
                if (mapping.get("current_topic_id"), mapping.get("current_subtopic_id")) != (pt.get("topic_id"), pt.get("subtopic_id")):
                    raise InputValidationError(f"Frozen mapping baseline mismatch: {pt_id}")
                expected_classification = (mapping["proposed_topic_id"], mapping["proposed_subtopic_id"])
            else:
                expected_classification = (pt.get("topic_id"), pt.get("subtopic_id"))
            if all(expected_classification) and (topic_id, subtopic_id) != expected_classification:
                raise InputValidationError(f"Classification index differs from frozen classification: {pt_id}")

            # Validate against proposed taxonomy structure if available
            if proposed_taxonomy_topics is not None:
                if topic_id not in proposed_taxonomy_topics:
                    raise InputValidationError(f"Proposed topic_id '{topic_id}' for '{pt_id}' not in proposed taxonomy")
                if subtopic_id not in proposed_taxonomy_topics[topic_id]:
                    raise InputValidationError(
                        f"Proposed subtopic_id '{subtopic_id}' for '{pt_id}' not under topic '{topic_id}' in proposed taxonomy"
                    )

            # Classify domain vs subtopic extension
            if topic_id not in CORE_TOPIC_IDS:
                new_domain_count += 1
            elif not pt.get("topic_id") or not pt.get("subtopic_id"):
                existing_domain_new_subtopic_count += 1

            source_page = format_source_page(pt.get("source_pages"))
            source_section = pt.get("source_section")
            summary_es = pt.get("summary_es", "").strip()
            qualifications = list(pt.get("qualifications_es", []))

            # Preserve known canonical statement_type if supplied, otherwise explicit_proposal
            statement_type = pt.get("statement_type") or "explicit_proposal"

            stmt = StatementRecord(
                schema_version="1.0.0",
                election_id=election_id,
                id=pt_id,
                party_id=src_info.party_id,
                programme_id=src_info.programme_id,
                topic_id=topic_id,
                subtopic_id=subtopic_id,
                statement_type=statement_type,
                summary=summary_es,
                summary_en=None,
                quote=None,  # STRICT: NO quote or evidence excerpt in statement fields
                source_url=src_info.source_url,
                source_version=src_info.source_version,
                source_page=source_page,
                source_section=source_section,
                qualifications=qualifications,
                policy_instrument=None,
                reviews=[],  # STRICT: reviews empty, draft status only
                review_status="draft",
                last_reviewed_date=None,  # STRICT: no forged dates
                correction_id=None,
                is_fixture=False,
            )

            raw_evidence = pt.get("evidence", [])
            evidence_records = [
                {
                    "pdf_page": ev.get("pdf_page"),
                    "excerpt": ev.get("excerpt"),
                    "text_sha256": ev.get("text_sha256"),
                }
                for ev in raw_evidence
            ]

            evidence_obj = {
                "statement_id": pt_id,
                "party_id": src_info.party_id,
                "source_id": src_info.source_id,
                "source_sha256": src_info.source_sha256,
                "source_pages": pt.get("source_pages", []),
                "source_section": source_section,
                "evidence": evidence_records,
            }

            in_memory_records.append(
                {
                    "pt_id": pt_id,
                    "party_id": src_info.party_id,
                    "source_id": src_info.source_id,
                    "stmt": stmt,
                    "evidence_obj": evidence_obj,
                    "evidence_records": evidence_records,
                    "topic_id": topic_id,
                    "subtopic_id": subtopic_id,
                    "source_page": source_page,
                    "source_section": source_section,
                    "baseline_topic_id": pt.get("topic_id"),
                    "baseline_subtopic_id": pt.get("subtopic_id"),
                }
            )

    # Verify classification index has NO extra rows
    if len(proposed_map) != total_canonical_points:
        raise InputValidationError(
            f"Classification index row count mismatch: index has {len(proposed_map)} rows, but canonical points total {total_canonical_points}"
        )

    # 7. Atomic staging to private temporary sibling directory with 0700 permissions
    out_path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    tmp_staging_dir = Path(tempfile.mkdtemp(prefix=f".tmp-staging-{out_path.name}-", dir=out_path.parent))

    try:
        os.chmod(tmp_staging_dir, 0o700)

        statements_dir = tmp_staging_dir / "statements"
        evidence_dir = tmp_staging_dir / "evidence"
        statements_dir.mkdir(mode=0o700)
        evidence_dir.mkdir(mode=0o700)
        os.chmod(statements_dir, 0o700)
        os.chmod(evidence_dir, 0o700)

        staged_manifest_entries: list[dict[str, Any]] = []
        evidence_index: dict[str, Any] = {}
        classification_proposal_ledger: list[dict[str, Any]] = []
        total_evidence_excerpts = 0

        for rec in in_memory_records:
            pt_id = rec["pt_id"]
            stmt = rec["stmt"]
            evidence_obj = rec["evidence_obj"]
            evidence_records = rec["evidence_records"]
            filename = f"{pt_id}.json"

            stmt_file = statements_dir / filename
            stmt_dict = asdict(stmt)
            stmt_file.write_text(
                json.dumps(stmt_dict, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.chmod(stmt_file, 0o600)

            ev_file = evidence_dir / filename
            ev_file.write_text(
                json.dumps(evidence_obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.chmod(ev_file, 0o600)

            total_evidence_excerpts += len(evidence_records)

            evidence_index[pt_id] = {
                "evidence_ref": f"evidence/{filename}",
                "evidence_hashes": [e["text_sha256"] for e in evidence_records if e.get("text_sha256")],
                "excerpt_count": len(evidence_records),
            }

            classification_proposal_ledger.append(
                {
                    "statement_id": pt_id,
                    "party_id": rec["party_id"],
                    "baseline_topic_id": rec["baseline_topic_id"],
                    "baseline_subtopic_id": rec["baseline_subtopic_id"],
                    "proposed_topic_id": rec["topic_id"],
                    "proposed_subtopic_id": rec["subtopic_id"],
                    "status": "proposal_only",
                    "human_approval_granted": False,
                }
            )

            staged_manifest_entries.append(
                {
                    "id": pt_id,
                    "party_id": rec["party_id"],
                    "topic_id": rec["topic_id"],
                    "subtopic_id": rec["subtopic_id"],
                    "source_locator": {"page": rec["source_page"], "section": rec["source_section"]},
                    "review_fingerprint": stmt.review_fingerprint(),
                    "evidence_ref": f"evidence/{filename}",
                    "evidence_hashes": [e["text_sha256"] for e in evidence_records if e.get("text_sha256")],
                }
            )

        ev_index_file = tmp_staging_dir / "evidence-index.json"
        ev_index_file.write_text(
            json.dumps(evidence_index, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(ev_index_file, 0o600)

        prop_file = tmp_staging_dir / "classification-proposal.json"
        prop_file.write_text(
            json.dumps(
                {
                    "package": "E1.4-2026",
                    "human_approval_granted": False,
                    "taxonomy_status": "proposal_only",
                    "statement_count": len(classification_proposal_ledger),
                    "proposals": classification_proposal_ledger,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        os.chmod(prop_file, 0o600)

        staging_manifest = {
            "package": "E1.4-2026",
            "election_id": manifest_data.get("election_id", "es-gen-2026"),
            "human_approval_granted": False,
            "review_status": "draft",
            "is_fixture": False,
            "source_count": len(verified_sources),
            "statement_count": len(staged_manifest_entries),
            "evidence_excerpt_count": total_evidence_excerpts,
            "source_metadata_binding_verified": True,
            "original_archive_audit_verified": archive_audit_verified,
            "sources": [
                {
                    "party_id": s.party_id,
                    "source_id": s.source_id,
                    "programme_id": s.programme_id,
                    "source_sha256": s.source_sha256,
                    "points_count": s.points_count,
                    "points_sha256": s.points_sha256,
                    "coverage_sha256": s.coverage_sha256,
                    "source_url": s.source_url,
                    "source_version": s.source_version,
                    "metadata_binding_verified": True,
                    "original_archive_audit_verified": s.original_archive_audit_verified,
                }
                for s in verified_sources
            ],
            "statements": staged_manifest_entries,
        }

        manifest_out = tmp_staging_dir / "staging-manifest.json"
        manifest_out.write_text(
            json.dumps(staging_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(manifest_out, 0o600)

        status_data = {
            "package": "E1.4-2026",
            "stage": "publication-preparation/private-record-staging",
            "status": "success",
            "human_approval_granted": False,
            "source_count_verified": len(verified_sources),
            "statement_count_staged": len(staged_manifest_entries),
            "evidence_excerpts_preserved": total_evidence_excerpts,
            "new_domain_count": new_domain_count,
            "existing_domain_new_subtopic_count": existing_domain_new_subtopic_count,
            "quotes_in_statement_fields": 0,
            "review_marks_granted": 0,
            "is_fixture": False,
            "review_status": "draft",
            "generator_rejection_expected": True,
            "source_metadata_binding_verified": True,
            "original_archive_audit_verified": archive_audit_verified,
            "output_directory": str(out_path),
            "permissions": {"directories": "0700", "files": "0600"},
            "limits": [
                "All staged statements strictly have review_status='draft' and reviews=[]",
                "No human approvals or review marks are granted (human_approval_granted=false)",
                "Evidence excerpts are excluded from statement fields and preserved privately separately by reference and text hash",
                "Exact page coordinates are preserved with gaps comma-separated; contiguous ranges only",
                "Proposed taxonomy classifications (12 topics / 64 subtopics) are recorded as private proposals only",
                "The production build requires recorded human approval for each draft summary",
            ],
        }

        status_out = tmp_staging_dir / "status.json"
        status_out.write_text(
            json.dumps(status_data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(status_out, 0o600)

        # Atomic rename
        os.rename(tmp_staging_dir, out_path)
        os.chmod(out_path, 0o700)

    except Exception:
        if tmp_staging_dir.exists():
            shutil.rmtree(tmp_staging_dir, ignore_errors=True)
        raise

    return StagingResult(
        run_dir=run_path,
        output_dir=out_path,
        source_count=len(verified_sources),
        statement_count=len(staged_manifest_entries),
        evidence_count=total_evidence_excerpts,
        new_domain_count=new_domain_count,
        existing_domain_new_subtopic_count=existing_domain_new_subtopic_count,
        manifest_path=out_path / "staging-manifest.json",
        status_path=out_path / "status.json",
        original_archive_audit_verified=archive_audit_verified,
        human_approval_granted=False,
    )


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint for private draft staging utility."""
    parser = argparse.ArgumentParser(
        description="E1.4-2026: Stage private draft inventories into schema-shaped draft records."
    )
    parser.add_argument("--run-dir", required=True, type=Path, help="Path to private review run directory")
    parser.add_argument("--output-dir", required=True, type=Path, help="Path to staging output directory (outside repo)")
    parser.add_argument("--repo-root", default=None, type=Path, help="Path to repo root (defaults to auto-detected)")

    args = parser.parse_args(argv)

    try:
        result = stage_corpus(
            run_dir=args.run_dir,
            output_dir=args.output_dir,
            repo_root=args.repo_root,
        )
        print(
            f"Successfully staged {result.statement_count} statements from {result.source_count} sources "
            f"to {result.output_dir} (human_approval_granted=False, original_archive_audit_verified={result.original_archive_audit_verified})."
        )
        return 0
    except CorpusStagingError as e:
        print(f"Staging error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
