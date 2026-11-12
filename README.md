# Elections 2026 — Project draft

This project will compare official party programmes for the Spanish general election on 29 November 2026. The date comes from [BOE-A-2026-20742](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742).

**Status (2026-10-12):** The static comparator and authenticated private hosting exist. PR #68 adds the mock quiz foundation. The 2023 political content is withdrawn pending authentic human review. The public site and real quiz are not approved for release.

Use the [GitHub task index](https://github.com/c2ventures/elecciones2026/issues/78) for remaining work. See the [current pilot audit](docs/PILOT-2023-AUDIT.md) for the content boundary.

## MVP

The Spanish-language, mobile-first site will compare reviewed programme statements by topic. Each statement will link to its source document, page or section, and version. The site will show missing source data as missing data, not as a party position. See [ROADMAP.md](ROADMAP.md) and the [OpenSpec MVP change](openspec/changes/mvp-programme-comparison/).

The [2026-10-09 source check](docs/SOURCE-AVAILABILITY-2026.md) lists official discovery paths. No complete 2026 general-election programme was verified in that bounded check; older national and 2026 regional programmes are not substitutes.

A separate, clearly labelled 2023 proof of concept may use official 2023 general-election sources after rights and editorial checks. Election IDs prevent a 2023 source from appearing as a 2026 programme. The application code can transfer; programme records and reviewed claims cannot.

The MVP uses the Stitch screens as a visual starting point, but it includes only home, one-topic/two-party selection, a comparison grouped by measure, and a concise source/method page. The [delivery roadmap](openspec/ROADMAP.md) defines epics, milestones, and agent-sized work packages. The quiz follows the MVP; the seat simulator, CIS data, and localization follow in separate changes.

A later [commitment follow-through proposal](openspec/changes/commitment-follow-through/proposal.md) is exploratory. It can be rejected if comparable evidence or a neutral method is not available. No party "lies" percentage is planned for the MVP.

## Technical plan

Python 3.14 validates editorial records and generates static HTML, CSS, JavaScript, and JSON. Docker serves the static output. Document extraction runs in a separate offline environment. The public container will not contain a database, PDF parser, or editorial credentials. Use FastAPI only if a later change needs a server API.

The active target is an IONOS Ubuntu VPS with 1 vCPU and 1 GB RAM. Cloudflare proxies the authenticated preview. Private delivery passed external content verification. Live capacity, monitoring, recovery, and public release checks remain open. See [the verified server setup](ops/SERVER-MIGRATION.md). Hetzner is a later migration option.

## Preview

Run `docker compose up --build` and open `http://localhost:8080`. The default build uses the separate `es-gen-2026` production corpus and keeps the quiz unavailable. Source documents are registered; programme claims remain pending editorial review. Add reviewed records through the [2026 corpus workflow](content/elections/es-gen-2026/README.md). Use `ELECTION_ID=es-gen-2023` for the explicit historical rehearsal, or `QUIZ_MODE=mock` only for a private fictional quiz preview. The serving image is pinned by digest. CI checks non-root, read-only serving and image parity.

Human statement, comparison, and source-rights reviews are required before 2023 claims can return. Political content must come from approved records in both HTML and browser output. A historical rehearsal does not pass G2 for 2026.

The public interface and editorial content are in Spanish. Repository documents, specifications, code, and comments are in English. See [writing standard](docs/WRITING-STANDARD.md).

## Licence and contributions

Original project code and documentation are under [Apache-2.0](LICENSE). See [NOTICE](NOTICE) for provisional C2 Ventures attribution and the boundary for third-party electoral material. Programme documents, extracts, party marks, and other third-party content are not relicensed by this repository. Before public release, the project owners must confirm the exact copyright holder name and rights for every published source or asset.

See [contribution rules](CONTRIBUTING.md) and [agent rules](AGENTS.md). Use a roadmap package in each pull request, short Conventional Commits, and a concise Why/What pull request description.

Private editorial source processing is documented in [the private archive workflow](docs/PRIVATE-SOURCE-ARCHIVE.md). Originals and full extracted text stay outside Git and public artifacts; archive verification does not approve political claims.
