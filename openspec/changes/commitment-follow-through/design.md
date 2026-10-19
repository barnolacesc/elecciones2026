# Design: Prior commitment follow-through

Roadmap package: **E9.1–E9.4**. Exploratory track; human editorial signoff, inter-reviewer audit, and Gate G9 remain open.

## Context

See [proposal.md](proposal.md) and the capability specifications in [specs/commitment-evidence-register/spec.md](specs/commitment-evidence-register/spec.md) and [specs/follow-through-method/spec.md](specs/follow-through-method/spec.md).

Voters comparing 2026 electoral programmes often demand context on past performance: did parties fulfill their prior promises, compromise, stall, or take actions directly contrary to what they campaigned on? However, attempting to answer this by labeling broken promises as "lies" or calculating aggregate "honesty percentages" introduces fatal methodological traps (mens rea presumption, power asymmetry between government and opposition, cherry-picking bias, and reliance on partisan media).

This design establishes a reproducible, offline-first methodology and data architecture that links prior commitments (starting with the 2023 general election) to sovereign primary records (*Boletín Oficial del Estado* and *Boletín Oficial de las Cortes Generales*), with strict institutional attribution and zero subjective rhetoric.

## Goals / Non-Goals

**Goals:**
- A schema-governed commitment register linking prior manifesto pledges to primary sovereign gazettes (BOE, BOCG, IGAE).
- Clear segregation of institutional roles (governing vs. opposition) to prevent structural bias.
- An objective 8-state status taxonomy without evaluative adjectives or "lie" labels.
- Symmetrical, expandable mobile presentation (360–430 CSS px) within proposal comparison views.
- An offline 10-measure pilot benchmark to validate inter-reviewer agreement before touching public generator logic.

**Non-Goals:**
- Calculating an aggregate "honesty score" or "percentage of fulfilled promises".
- Evaluating subjective political intentions or psychological motives.
- Citing media articles, opinion columns, or press releases as primary evidence.
- Replacing or delaying the MVP comparator (G4), quiz (G5), or seat simulator (G6).

## Decisions

### 1. Data Schema and Record Granularity

Store commitment records as versioned JSON files under `content/commitments/` (e.g. `cmt-2023-psoe-housing-001.json`).

```json
{
  "$schema": "../../schemas/commitment.schema.json",
  "id": "cmt-2023-psoe-housing-001",
  "election_id": "es-gen-2023",
  "party_id": "psoe",
  "topic_id": "housing",
  "pledge": {
    "summary_es": "Creación de un parque público de 50.000 viviendas de alquiler asequible.",
    "verbatim_quote": "Desarrollaremos un plan para la incorporación de 50.000 viviendas de alquiler asequible...",
    "source_id": "src-2023-psoe-prog",
    "page": 48,
    "section": "Medida 12"
  },
  "governance_context": {
    "role": "governing_senior",
    "legislature": "XV",
    "period_start": "2023-11-17",
    "period_end": "2026-10-01",
    "jurisdiction": "state"
  },
  "status": "partially_enacted",
  "evidence": [
    {
      "source_type": "boe",
      "official_id": "BOE-A-2024-5172",
      "title": "Resolución de 14 de marzo de 2024, índice de precios de alquiler",
      "url": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-5172",
      "date": "2024-03-15",
      "finding_summary_es": "Aprobación del sistema estatal de referencia del precio del alquiler y acuerdos ICO-MIVAU."
    }
  ],
  "editorial_review": {
    "drafter": "researcher-01",
    "reviewed_by_1": "auditor-citation-01",
    "reviewed_by_2": "auditor-neutrality-02",
    "lead_editor_signoff": "editor-in-chief",
    "review_date": "2026-10-15",
    "agreement_status": "unanimous"
  }
}
```

### 2. Institutional Attribution Rules

| Party Status | Power Exercised | Evaluative Basis | Primary Source |
|---|---|---|---|
| **Governing Party** (Sole or Senior) | Executive decrees, legislative agenda, budget allocation | Enacted laws, Royal Decree-laws, budget execution | BOE, IGAE |
| **Governing Junior Partner** | Co-sponsor of government bills; specific ministerial portfolios | Ministerial initiatives, coalition agreement alignment | BOE, Coalition pact |
| **Opposition Party** | Parliamentary voting, legislative motions | Roll-call votes (*votaciones nominales*) on matching bills | BOCG, *Diario de Sesiones* |

**Constraint:** An opposition party cannot be classified as failing to execute an executive decree. If an opposition party pledged measure $X$, the platform audits whether they registered a *Proposición de Ley* or how their parliamentary group voted when bill $X$ reached the chamber floor.

### 3. The 8-State Follow-Through Taxonomy

1. `enacted_as_pledged` (*Cumplida según programa*)
2. `partially_enacted` (*Parcialmente cumplida*)
3. `contrary_action_taken` (*Acción contraria documentada*)
4. `coalition_compromise` (*Modificada por pacto de gobierno*)
5. `blocked_by_parliament` (*Iniciada pero rechazada por mayoría parlamentaria*)
6. `no_initiative_registered` (*Sin iniciativa registrada en la legislatura*)
7. `outside_state_competence` (*Competencia no estatal / autonómica*)
8. `unassessable` (*Evidencia no concluyente / datos insuficientes*)

### 4. Sovereign Source Hierarchy

To eliminate accusations of political bias:
1. **Tier 1 (Sovereign Primary):** *Boletín Oficial del Estado* (BOE), *Boletín Oficial de las Cortes Generales* (BOCG), *Diario de Sesiones del Congreso*.
2. **Tier 2 (Official Institutional):** IGAE, Tribunal de Cuentas, INE, Eurostat, Consejo de Ministros formal references.
3. **Strictly Prohibited:** Commercial newspapers (El País, El Mundo, ABC, elDiario.es, etc.), partisan blogs, televised debates, opinion polls, or social media statements.

### 5. Mobile UI Component: Expandable Precedent Disclosure

In the mobile comparator (`360–430 CSS px`):
- 2026 proposals remain the primary unencumbered content.
- When an historical precedent exists, an accessible disclosure (`<details>` or button with `aria-expanded`) renders with a minimum 44 px touch target.
- Label: `"Antecedente en la legislatura previa (2023–2026)"`.
- Expanded content displays:
  - Exact 2023 pledge text + page/section link.
  - Institutional role badge (`Gobierno de coalición` or `Oposición parlamentaria`).
  - Audited status badge with neutral styling.
  - Factual bullet points linking directly to the BOE or BOCG.
  - Symmetrical layout: competing parties appear side-by-side with equal space.

## Bounded Packages

| Package | Scope | Deliverables & Exit Criteria | Depends On |
|---|---|---|---|
| **E9.1** | Methodology and schema contract | Complete schema `commitment.schema.json`, status vocabulary, attribution rules, and review guidelines. | G4 |
| **E9.2** | 10-Measure benchmark pilot dossier | Offline dossier of 10 real-world 2023 commitments (5 governing, 5 opposition) mapped to BOE/BOCG citations. | E9.1 |
| **E9.3** | Inter-reviewer agreement audit & go/no-go | Dual-review audit testing coding consistency across reviewers; formal Gate G9 decision on public viability. | E9.2 |
| **E9.4** | Generator integration & mobile UI | Static Python generator integration, mobile UI disclosure card, accessibility verification. | E9.3, human signoff |

## Risks / Trade-offs

- **[Voter misunderstanding of opposition role]** → Clear, explicit UI badge explaining that opposition parties are audited on parliamentary votes, not executive decrees.
- **[Allegations of cherry-picking]** → Complete prohibition of party-wide percentage scores; clear disclosure that precedents are shown per-measure where direct continuity exists.
- **[Disputed legislative outcomes]** → Dual-review protocol with mandatory citation to BOE/BOCG gazette numbers; unresolved cases default to `unassessable`.
