# P2 source-journey audit — 2026-10-23

**Package:** P2 / E2.4–E2.5 reader-facing source gate. **Baseline:** `origin/main` at `fe5e05e`. **Status:** implementation handoff, not an editorial or accessibility approval.

## Reproducible baseline

- `content/sources/register.json` has four `es-gen-2023` rows (PP, ERC, PNV, Sumar), all `published-unverified`, and nine `es-gen-2026` rows, all `missing`. These counts are register rows, not a complete candidature denominator or approved programme coverage.
- `render_sources_page` in `src/elecciones2026/generator.py` places the 2026 section before the 2023 section even when `ctx.election_id` is `es-gen-2023`. Its 2023 notice says the documents are used *exclusively* for technical schema tests. That wording and prominence need review against the current 2023-first private-pilot scope; the active election must not be confused with future 2026 coverage.
- `render_source_coverage_card` and the desktop sources table use the generic label `Enlace oficial` whenever `official_url` exists. The nine 2026 `missing` rows can therefore link to official party/discovery pages without an identified programme. The label does not tell a reader whether the destination is a programme document or a discovery page. A URL alone does not validate a programme, quotation rights, or publication status.
- The existing E2.4 test checks the presence of `Enlace oficial` and source cards. It does not distinguish programme-document links from discovery links or assert active-election ordering. The existing browser acceptance checks mobile navigation and outbound link attributes, not this distinction.
- PR #101 is draft/conflicting and changes `render_source_coverage_card` rights wording in the same generator function. Its prior green CI is not a human rights decision. PRs #125, #128 and #129 separately own result focus, sharing and quiz result scope. This audit changes none of those surfaces.

Reproduction from a clean checkout:

```sh
node - <<'NODE'
const fs = require('fs');
const register = JSON.parse(fs.readFileSync('content/sources/register.json', 'utf8'));
for (const election of ['es-gen-2023', 'es-gen-2026']) {
  const rows = register.sources.filter(source => source.election_id === election);
  console.log(election, rows.length, [...new Set(rows.map(source => source.status))].join(','));
}
const generator = fs.readFileSync('src/elecciones2026/generator.py', 'utf8');
const page = generator.slice(generator.indexOf('def render_sources_page('), generator.indexOf('def render_corrections_page('));
console.log('2026 section before 2023:', page.indexOf('Fuentes monitorizadas · Elecciones Generales 2026') < page.indexOf('Fuentes históricas de ensayo · Piloto 2023'));
console.log('generic source link label:', generator.slice(generator.indexOf('def render_source_coverage_card('), generator.indexOf('def render_party_card(')).includes('Enlace oficial'));
NODE
```

## Acceptance handoff (not implemented here)

1. On an `es-gen-2023` sources route, identify the active election and its provisional/private coverage first. Keep the 2026 register visibly separate as future discovery data. Do not change canonical election IDs or claim the four-row pilot is complete.
2. Label every outbound target by *what it actually is*: programme PDF/document only when a registered document URL and version support that label; otherwise party or discovery page. Preserve a readable missing/partial/unverified state beside the link. A missing document must never become a negative party position.
3. Make source rights, hash, version and retrieval fields understandable without implying that `published-unverified` is editorial approval. Keep link/source labels consistent between the mobile cards, desktop table and any party-detail link. Do not infer rights or alter the source register.
4. Add generated-output regression assertions for both election contexts and link types. At 360, 390 and 430 CSS px, traverse home or a deep comparison → source card → original destination (without following an external link in automated tests); verify keyboard order, visible focus, no horizontal overflow, at least 44 CSS px targets and an unambiguous return CTA. Record actual-device/screen-reader observations separately. Passing CI is not that human review.

**Dependency:** coordinate the renderer hunk with PR #101's owner before implementation. P0 inclusion, rights and editorial decisions remain with their owners. No source record, political claim, approval, PDF, public artifact, routing or release was changed by this audit.
