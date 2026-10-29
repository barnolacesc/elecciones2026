# 2023 shared-document attribution: repository audit

Roadmap package: **P0.10**, `2023-corpus-completion` (proposal only).
Election: `es-gen-2023`. Checked `origin/main` at `8e2fab4` on 2026-10-29.
This audits repository contracts, not publisher sites, private PDFs or human
editorial decisions.

## Observed boundary

- `content/sources/register.json` has four 2023 pilot source rows (PP, ERC,
  PNV, Sumar). Each has one `party_id` and `candidature_name`; all four have
  `published-unverified`, `rights_review.status=not_reviewed` and a null
  publication date. These are pilot records, not the approved 2023 manifest.
- `content/sources/register.schema.json` requires a singular `party_id` per
  source row; `content/schemas/programme.schema.json` requires a singular
  `candidacy_id` per programme. Neither contract records an independently
  reviewed document-to-candidature applicability edge or its constituency,
  version and evidence. No shared-document case is evidenced by the pilot.
- The P0.2 design drafts a candidature-to-document join, and P0.3 identifies
  corrected constituency and coalition names. It does not settle how one
  identical programme version may be applicable to several ballot lists while
  preserving one document identity and separate scope decisions. The existing
  P1 document-scope draft PR #150 addresses which documents are relevant to a
  topic search; this package addresses *which candidature may use a document*
  before that search. Neither is approved.
- PR #101 remains open, conflicting and without GitHub reviews; PR #166 is a
  mergeable replacement candidate with failing CI jobs. Its PR body reports
  a GitHub billing/spending-limit block rather than completed test execution.
  Neither supplies a 2023 inclusion rule, a document-to-candidature approval,
  rights approval or editorial signoff. The merged 2023-first roadmap is PR
  #113. Recent CI status is engineering evidence, not human review.

## Proposed decision boundary

Record the physical/versioned source once, then review each applicability edge
from that source to an approved candidature manifest row. An edge needs the
election, rule/manifest revision, exact source version/hash, candidature and
constituency scope, document role, evidence reference, reviewer and decision.
`candidate` and `pending` edges must not count as coverage. A coalition's
programme does not automatically become a member party's independent position;
same bytes at multiple URLs do not establish equal scope or rights.

This proposal does not change the current singular pilot schema or assert that
any actual 2023 source is shared. It proposes a later reviewable join, not a
completed inventory, rights decision or published political claim.

## Decisions for owner and editorial review

1. Approve the 2023 candidature identity and coalition/territorial inclusion
   rule before resolving any shared-document edge.
2. Choose the evidence and reviewers for publisher intent, geographical and
   ballot-list applicability, including ambiguous coalition/member cases.
3. Decide how to present shared documents and counts without double-counting
   distinct documents, deduplicating candidatures, or implying two parties
   independently endorsed the same measure.

No PDF, source row, programme record, political statement, rights status,
review mark or public artifact changed in this audit.
