# Elections 2026 — Project draft

This project will compare official party programmes for the Spanish general election on 29 November 2026. The date comes from [BOE-A-2026-20742](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742).

**Status:** planning scaffold only. No party data, working comparator, or deployment exists. The visual preview uses fictional parties and text.

## MVP

The Spanish-language, mobile-first site will compare reviewed programme statements by topic. Each statement will link to its source document, page or section, and version. The site will show missing source data as missing data, not as a party position. See [ROADMAP.md](ROADMAP.md) and the [OpenSpec MVP change](openspec/changes/mvp-programme-comparison/).

The [2026-10-09 source check](docs/SOURCE-AVAILABILITY-2026.md) lists official discovery paths. No complete 2026 general-election programme was verified in that bounded check; older national and 2026 regional programmes are not substitutes.

A separate, clearly labelled 2023 proof of concept may use official 2023 general-election sources after rights and editorial checks. Election IDs prevent a 2023 source from appearing as a 2026 programme. The application code can transfer; programme records and reviewed claims cannot.

The MVP uses the Stitch screens as a visual starting point, but it includes only home, one-topic/two-party selection, a comparison grouped by measure, and a concise source/method page. The [delivery roadmap](openspec/ROADMAP.md) defines epics, milestones, and agent-sized work packages. The quiz follows the MVP; the seat simulator, CIS data, and localization follow in separate changes.

A later [commitment follow-through proposal](openspec/changes/commitment-follow-through/proposal.md) is exploratory. It can be rejected if comparable evidence or a neutral method is not available. No party "lies" percentage is planned for the MVP.

## Technical plan

Python 3.14 will validate editorial records and generate static HTML, CSS, JavaScript, and JSON. Docker will serve the static output in local preview and production. Document extraction will run in a separate offline environment. The public container will not contain a database, PDF parser, or editorial credentials. Use FastAPI only if a later change needs a server API.

The initial target is a Hetzner VM with about 2 vCPU and 8 GB RAM. Cloudflare Free will provide DNS and a proxy/edge layer, subject to verified plan limits. This target is not a capacity guarantee. Load tests must verify any concurrency goal before release.

## Preview

Run `docker compose up --build` and open `http://localhost:8080`. This environment has no Docker executable, so this command has not been verified here. The current base image tag is provisional. Pin it by digest, scan it, and review it before production.

The public interface and editorial content are in Spanish. Repository documents, specifications, code, and comments are in English. See [writing standard](docs/WRITING-STANDARD.md).

## Licence and contributions

Original project code and documentation are under [Apache-2.0](LICENSE). See [NOTICE](NOTICE) for provisional C2 Ventures attribution and the boundary for third-party electoral material. Programme documents, extracts, party marks, and other third-party content are not relicensed by this repository. Before public release, the project owners must confirm the exact copyright holder name and rights for every published source or asset.

See [contribution rules](CONTRIBUTING.md) and [agent rules](AGENTS.md). Use a roadmap package in each pull request, short Conventional Commits, and a concise Why/What pull request description.

Private editorial source processing is documented in [the private archive workflow](docs/PRIVATE-SOURCE-ARCHIVE.md). Originals and full extracted text stay outside Git and public artifacts; archive verification does not approve political claims.
