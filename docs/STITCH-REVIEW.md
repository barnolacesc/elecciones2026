# Stitch design review — 2026-10-09

## Input

The user provided a ZIP file with seven PNG screens, seven generated HTML files, and one design-system document. The ZIP file was inspected as reference data only. No generated script was run. The original files remain outside the project repository in a local review folder.

## Decision

Use the **comparison grouped by measure** screen as the mobile MVP reference. It places both party positions under the same measure. This structure supports direct comparison better than a tab view, which hides one party at a time. Do not use tab switches in the MVP.

Use the home, selection, source coverage, statement detail, and method screens as visual references. Replace the permanent bottom navigation bar with a compact top header and footer to preserve vertical space on mobile viewports. Remove the profile icon completely: the MVP has no user accounts.

The complete component plan and mobile wireframes are codified in [`site/COMPONENT-PLAN.md`](../site/COMPONENT-PLAN.md). Local design tokens are codified in [`site/tokens/tokens.json`](../site/tokens/tokens.json) and [`site/tokens/tokens.css`](../site/tokens/tokens.css).

## Resolution of changes required before implementation (Package E2.1)

1. **Fictional content isolation:** All fictional quotes, claims, record IDs, and download links in Stitch are classified as reference mockups. The component plan uses explicit placeholder labels (`Partido A (ficticio)`, `Programa de ejemplo`) until official sources are ingested via package E1.4.
2. **Density and structure on comparison screen:** The grouped comparison flow shows a short neutral measure summary, followed by vertically stacked party position cards with source citations in the same flow.
3. **Factual provenance over deceptive verification:** Removed all claims such as “100% verificado”. Statements expose factual citations (document, version, page, and review date). Negative evidence is explicitly marked as `no consta` ("No consta posición en el programa analizado"), preventing confusion with political opposition.
4. **Zero external CDN dependencies:** Eliminated Tailwind CDN, Google Fonts, and external image dependencies. The project uses local design tokens (`--color-*`, `--space-*`, `--font-*`) and native system font stacks.
5. **Mobile viewport verification at 360, 390, and 430 CSS px:** Codified single-column wireframes across 360 px (compact phone), 390 px (baseline phone), and 430 px (large phone). All interactive controls strictly enforce touch targets of at least 44 CSS px (WCAG 2.5.5 / 2.5.8).
6. **Removal of interactive report form:** The static site has no backend database or write API. Removed the interactive discrepancy form. Replaced it with a clear informational notice stating that error reporting is planned for a later phase.

## Design system mapping

| Stitch Mockup Feature | Elecciones 2026 Architecture | Design Token / Specification |
|---|---|---|
| Tailwind CDN utility classes | Local CSS Custom Properties | `site/tokens/tokens.css` |
| Google Fonts (Inter web font) | System sans-serif stack | `var(--font-family-sans)` |
| Arbitrary brand colors | Calm civic neutral palette | `var(--color-bg-canvas)`, `var(--color-bg-primary)` |
| Party brand colors / logos | Neutral soft tint identifiers | `var(--color-party-a-*)`, `var(--color-party-b-*)` |
| "100% verificado" badge | Factual provenance link | `Component 7: PartyPositionCard` |
| Working feedback form | Static explanatory notice | `Component 11: MethodologyNotice` |
| User profile / account icon | Explicitly prohibited | `site/COMPONENT-PLAN.md` Section 6 |
| Multi-column comparison card | Stacked single-column card | Wireframes at 360, 390, 430 CSS px |

## Resolved design questions

- **Card structure:** Grouped measure cards with visible source links provide the most direct comparison without obscuring qualifications or party differences.
- **Coverage details:** The source coverage screen displays official document names, status badges (`Oficial`, `Parcial`, `No disponible`), retrieval dates, and SHA-256 hashes in a clean monospace block.
- **Navigation model:** Discarded permanent bottom navigation. Four MVP destinations fit cleanly in the top header and footer, maximizing screen space for policy text on mobile phones.

The Stitch design is a visual reference only, not an approved content source or production implementation.
