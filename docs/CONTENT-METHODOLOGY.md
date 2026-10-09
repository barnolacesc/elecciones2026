# Content and Editorial Methodology

**Document version:** 1.0.0  
**Effective date:** 2026-10-09  
**Status:** Draft policy submitted for human gate G0 approval.  
**Election identifier:** `es-gen-2026` (Spanish General Election, 29 November 2026)  
**Governing reference:** [BOE-A-2026-20742](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742)

---

## 1. Editorial Purpose and Boundaries

This methodology defines the operational rules for the election comparison platform. The platform helps citizens compare policy proposals from political parties for the 2026 Spanish general election.

### Core Principles

1. **Strict Neutrality:** The platform does not recommend votes, endorse candidates, or rank political parties.
2. **Traceability:** Every published statement must link to an official source document, version, page or section, and retrieval timestamp.
3. **Discrete Unit of Comparison:** The comparison unit is a specific policy proposal. A slogan or broad intention is not a valid comparison unit. A valid proposal states a functional objective, a policy instrument, eligibility conditions, funding mechanisms (when published), and administrative jurisdiction.
4. **Separation of Absence and Opposition:** When a reviewed document does not mention a topic, the platform records `not_found`. The platform must never present `not_found` as opposition or agreement.
5. **Independent Dual Review:** Two human reviewers must verify every extracted statement before publication. Automated extraction tools may propose text, but cannot publish text.

---

## 2. Candidate and Candidacy Inclusion Policy

The platform applies objective, predictable thresholds to select candidacies for coverage. This rule prevents arbitrary inclusion or exclusion.

### Inclusion Criteria

A political formation or electoral coalition qualifies for platform coverage if it meets at least one of the following two criteria:

1. **Parliamentary Representation Criterion (Criterion A):**
   - The party, federation, or coalition won at least one seat in the *Congreso de los Diputados* or *Senado* in the preceding general election (July 2023).
   - Alternatively, the party or coalition won at least one seat in the European Parliament elections of June 2024 across the single national constituency.
2. **National Proclamation Criterion (Criterion B):**
   - The *Junta Electoral Central* (JEC) officially proclaims candidacies for the formation in constituencies that represent at least 50% of the national registered electorate.

### Territorial and Regional Formations

Political formations that meet Criterion A but submit candidate lists only in specific autonomous communities (for example, ERC, EAJ-PNV, EH Bildu, Junts, BNG, CC) qualify for coverage. The platform must display the territorial scope of each regional candidacy so readers understand its ballot availability.

### Incomplete Coverage and Pre-publication Tracking

The platform adds every qualified formation to the coverage register immediately upon official election proclamation. If a qualified formation has not published an electoral programme, the platform does not exclude the formation. The platform records the formation with programme status `missing`.

---

## 3. Party and Candidacy Naming Standard

Political party names and coalition structures change across election cycles. To prevent confusion, every covered entity must use consistent, structured naming fields.

### Required Naming Fields

Every party or candidacy record must contain the following fields:

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | string | Unique, lowercase, hyphen-separated ASCII slug. Immutable for the election cycle. | `psoe`, `pp`, `vox`, `sumar` |
| `official_name` | string | Full legal name registered with the *Registro de Partidos Políticos* or proclaimed by the JEC. | `Partido Socialista Obrero Español` |
| `display_name` | string | Authoritative public name in Spanish. | `Partido Socialista Obrero Español` |
| `short_name` | string | Standard recognized acronym or short name. | `PSOE` |
| `ballot_name` | string | Official name printed on election ballots. | `PSOE` |
| `is_coalition` | boolean | True if the entity is an electoral coalition registered under electoral law. | `false` |
| `coalition_members` | list[string] | List of member party IDs if `is_coalition` is true; empty otherwise. | `[]` |
| `territorial_scope` | string | Geographic scope (`national` or autonomous community name). | `national` |

### Coalition Identity Rules

1. Electoral coalitions are election-specific legal entities under Spanish electoral law (*Ley Orgánica del Régimen Electoral General* - LOREG).
2. A 2026 coalition is legally distinct from a 2023 coalition of similar name. The platform must verify the official 2026 coalition registration filed with the JEC before linking historical records.
3. If political parties join or leave a coalition, the platform creates a new distinct record with an updated member list.
4. Member parties of a registered coalition do not receive separate standalone entries for constituencies where the coalition presents a joint list.

### Display and Ordering Rules

1. Selectors and comparison views must never sort parties by editorial preference, seat count, or poll results.
2. The default sort order is alphabetical by `display_name`.
3. An alternative objective sort order (such as parliamentary representation in the outgoing legislature) may be offered, but must be explicitly labelled.

---

## 4. Programme Status Lifecycle and Vocabulary

Every covered candidacy has a documented programme status. The platform uses six exact status values:

```
                  ┌──────────────┐
                  │   missing    │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  announced   │
                  └──────┬───────┘
                         │
                         ▼
        ┌──────────────────────────────────┐
        │       published-unverified       │
        └──────┬────────────────────┬──────┘
               │                    │
               ▼                    ▼
        ┌──────────────┐     ┌──────────────┐
        │   partial    │     │   official   │
        └──────┬───────┘     └──────┬───────┘
               │                    │
               └─────────┬──────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   replaced   │
                  └──────────────┘
```

### Status Definitions

1. `missing`:
   - **Definition:** The candidacy meets inclusion criteria, but no official 2026 general-election programme has been published or located on verified channels.
   - **Public presentation:** The platform displays an explicit banner: "Programa no disponible".
   - **Constraint:** The platform must not publish inferred statements for a candidacy with `missing` status.
2. `announced`:
   - **Definition:** The candidacy announced that a programme exists or will be presented (for example, through a press release or convention), but the complete document is not yet published or retrieved.
   - **Public presentation:** The platform displays a notice: "Programa anunciado; documento pendiente de publicación".
   - **Constraint:** Statements cannot be extracted or published until the source document is retrieved.
3. `partial`:
   - **Definition:** The candidacy published a preliminary document, thematic summary, manifesto of principles, or selected commitments, but not a full electoral programme.
   - **Public presentation:** The platform displays a label: "Programa parcial".
   - **Constraint:** Extracted statements must explicitly note the partial nature of the source document.
4. `published-unverified`:
   - **Definition:** A document was retrieved from a party channel, but editorial verification (URL confirmation, SHA-256 calculation, authenticity check, and rights review) is in progress.
   - **Public presentation:** Not visible on the public comparison views.
   - **Constraint:** Cannot support published comparison claims.
5. `official`:
   - **Definition:** The complete official electoral programme for the specific election, retrieved from primary party channels and verified with immutable URL, retrieval date, SHA-256 hash, and rights approval.
   - **Public presentation:** Full comparison active with link to the source document.
   - **Constraint:** Published statements must reference specific page or section coordinates.
6. `replaced`:
   - **Definition:** The political party published an updated version of a previously verified programme.
   - **Public presentation:** The older version is marked superseded.
   - **Constraint:** The predecessor record retains its historical metadata, records the successor ID in `superseded_by`, and triggers invalidation or re-review of dependent comparison records.

---

## 5. Topic Taxonomy (Version 1.0.0)

The topic taxonomy organizes policy proposals into clear, mutually exclusive categories. The taxonomy consists of 8 core topics.

### Version: 1.0.0

| ID | Spanish Name (`name_es`) | English Name (`name_en`) |
|---|---|---|
| `housing` | Vivienda | Housing |
| `education` | Educación | Education |
| `health-social-services` | Sanidad y servicios sociales | Health and Social Services |
| `economy-work-tax` | Economía, trabajo y fiscalidad | Economy, Work, and Tax |
| `immigration` | Inmigración | Immigration |
| `foreign-policy-eu` | Política exterior y Unión Europea | Foreign Policy and the EU |
| `climate-energy` | Clima y energía | Climate and Energy |
| `institutions-rights` | Instituciones, justicia y derechos fundamentales | Institutions, Justice, and Fundamental Rights |

---

### Detailed Topic Specifications

#### 1. `housing` (Vivienda)
- **Scope:** Rental market regulations, public housing stock construction and acquisition, mortgage relief, youth housing subsidies, urban land supply, eviction rules, and tourist accommodation limits.
- **Inclusion Boundaries:** Measures where the primary objective is housing affordability, supply, or tenancy rights.
- **Exclusion Boundaries:** General income tax brackets without specific housing earmarks (classify under `economy-work-tax`); residential care homes for dependent elderly people (classify under `health-social-services`).

#### 2. `education` (Educación)
- **Scope:** Public, state-subsidized (*concertada*), and private school funding; early childhood education (ages 0–3); university tuition fees and scholarships; vocational training (*Formación Profesional*); teacher ratios and working conditions; national curriculum standards; and language instruction in schools.
- **Inclusion Boundaries:** Educational institutions, instructional staff, students, and formal learning curricula.
- **Exclusion Boundaries:** General adult employment reskilling outside formal vocational systems (classify under `economy-work-tax`).

#### 3. `health-social-services` (Sanidad y servicios sociales)
- **Scope:** National Health System (*Sistema Nacional de Salud* - SNS) funding, primary care infrastructure, surgical and diagnostic waiting lists, mental health coverage, dental and optical public care, dependency system (*Sistema para la Autonomía y Atención a la Dependencia*), disability support, and eldercare facilities.
- **Inclusion Boundaries:** Healthcare delivery, public health protection, dependency care, and social assistance services.
- **Exclusion Boundaries:** Contributory and non-contributory retirement pensions (classify under `economy-work-tax`).

#### 4. `economy-work-tax` (Economía, trabajo y fiscalidad)
- **Scope:** Labor market regulations, statutory minimum wage (*Salario Mínimo Interprofesional* - SMI), working week duration and overtime, collective bargaining, income tax (*IRPF*), corporate tax (*Impuesto sobre Sociedades*), wealth and solidarity taxes, VAT (*IVA*), pension sustainability and indexation, public debt and deficit limits, and industrial policy.
- **Inclusion Boundaries:** Macroeconomic management, tax policy, employment law, pensions, and financial regulation.
- **Exclusion Boundaries:** Dedicated environmental taxes on emissions or plastics (classify under `climate-energy`).

#### 5. `immigration` (Inmigración)
- **Scope:** Administrative regularization processes, border enforcement and surveillance infrastructure, migrant reception centers, international protection and asylum procedures, nationality acquisition requirements, unaccompanied foreign minors (*MENA*), and labor migration permits.
- **Inclusion Boundaries:** Border control, international protection, migrant rights, and legal residency channels.
- **Exclusion Boundaries:** Broad diplomatic relations with third nations that do not focus primarily on migration governance (classify under `foreign-policy-eu`).

#### 6. `foreign-policy-eu` (Política exterior y Unión Europea)
- **Scope:** European Union treaties and fiscal framework compliance, Common Foreign and Security Policy, NATO commitments and defense expenditure, bilateral diplomacy (including Latin America and North Africa), development aid, international trade treaties, and multilateral peace missions.
- **Inclusion Boundaries:** Supranational diplomacy, defense pacts, European integration, and global treaties.
- **Exclusion Boundaries:** Domestic military legal codes or veterans' administrative benefits (classify under `institutions-rights`).

#### 7. `climate-energy` (Clima y energía)
- **Scope:** Greenhouse gas reduction targets, renewable energy generation and grid deployment, nuclear energy phase-out or extension, water management and drought infrastructure, electricity tariff regulation, industrial decarbonization, biodiversity protection, and circular economy.
- **Inclusion Boundaries:** Energy production, environmental conservation, emissions policy, and hydrological planning.
- **Exclusion Boundaries:** Residential insulation incentives framed strictly as housing subsidies (classify under `housing`).

#### 8. `institutions-rights` (Instituciones, justicia y derechos fundamentales)
- **Scope:** Constitutional reform, electoral law (*LOREG*) reform, judicial appointments (*Consejo General del Poder Judicial* - CGPJ), anti-corruption measures, transparency and freedom of information, civil service modernization, territorial administration and autonomous community financing (*Sistema de Financiación Autonómica* - SFA), gender equality, LGBTI+ rights, and civil liberties.
- **Inclusion Boundaries:** Constitutional governance, the judicial system, democratic integrity, regional financing, and human rights.
- **Exclusion Boundaries:** School curricula regarding civic education (classify under `education`).

---

### Classification and Disambiguation Rules

1. **Primary Operational Objective Rule:** When a policy proposal connects two topics (for example, "Tax exemption for youth rental housing"), the reviewer must assign the proposal to the topic matching its primary operational instrument. In this example, the primary instrument is housing assistance, so the topic is `housing`.
2. **Single Proposal Granularity:** Each extracted record must represent one discrete, testable proposal. Reviewers must not combine multiple distinct proposals from different topics into one record.
3. **Dispute Resolution:** When two reviewers propose different topic assignments for a proposal, the reviewers must record the disagreement in the editorial log. The lead editorial owner must resolve the dispute before publication.

---

## 6. Verification and Dual-Review Workflow

To ensure publication integrity, every published position follows a mandatory 5-step process:

1. **Extraction Proposal:** An offline extraction tool or human editor extracts the exact text, identifies the document, records page/section coordinates, and drafts a neutral Spanish summary.
2. **Source Integrity Check:** The editorial pipeline verifies that the document URL, retrieval date, SHA-256 hash, and publication rights record match the official registry.
3. **Neutral Phrasing Check:** The reviewer verifies that the summary does not use emotive, partisan, or evaluative adjectives. The summary must describe only the factual measure.
4. **Independent Secondary Review:** A second human reviewer verifies the proposal text against the original PDF/document context, checking for conditions, qualifications, and scope limits.
5. **Human Gate Approval:** Substantive claims are published only when both human reviews are recorded.

---

## 7. Correction and Invalidation Policy

1. **Immutable Identifiers:** Every published statement has an immutable identifier (for example, `stmt-psoe-housing-001`).
2. **Versioned Corrections:** If a factual or classification error occurs, the team publishes a dated correction record. The correction record identifies the affected statement ID, the previous text, the corrected text, the reason, and the reviewer.
3. **Invalidation of Dependent Comparisons:** When a source statement is corrected or a programme is marked `replaced`, all comparative relationships referencing that statement are marked invalidated until re-reviewed.
