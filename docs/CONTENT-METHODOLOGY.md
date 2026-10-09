# Content and Editorial Methodology

**Document version:** 1.1.0  
**Effective date:** 2026-10-09  
**Status:** Draft policy submitted for human gate G0 approval by project owners (Cesc and Project Partner). Roadmap packages E0.1 and E0.2 incorporated.  
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

## 6. Source Rights, Quotation Limits, and Verification Workflow

To protect legal integrity, editorial fairness, and citizen trust, every policy claim must satisfy strict intellectual property rules, quotation limits, and an independent dual-review process before publication.

---

### 6.1 Source Rights and Intellectual Property Framework

Electoral programmes published by political parties are intellectual creations protected under Spanish intellectual property law (*Real Decreto Legislativo 1/1996, de 12 de abril, por el que se aprueba el texto refundido de la Ley de Propiedad Intelectual* - TRLPI).

#### Governing Legal Principles

1. **Copyright Ownership:** Political parties, coalitions, and candidacies retain all moral and exploitation rights in their official programmes, manifestos, and published campaign documents, unless an express Creative Commons or public domain license is attached.
2. **Right of Quotation (*Derecho de Cita* - Art. 32 TRLPI):**
   - The platform reproduces excerpts of electoral programmes strictly pursuant to Article 32.1 TRLPI:
     > «Es lícita la inclusión en una obra propia de fragmentos de otras, ajenas de sentido plástico o fónico, y la de obras aisladas de carácter plástico o fotográfico figurativo, siempre que se trate de obras ya divulgadas y su inclusión se realice a título de cita o para su análisis, comentario o juicio crítico. Tal utilización sólo podrá realizarse con fines docentes o de investigación, en la medida justificada por el fin de esa incorporación e indicando la fuente y el nombre del autor de la obra utilizada.»
   - The platform’s analysis and comparison constitute public civic research and critical comparison of public campaign proposals.
3. **Prohibition of Third-Party PDF Hosting / Redistribution:**
   - To respect copyright and minimize bandwidth and legal exposure, the platform **MUST NOT** host, mirror, or redistribute complete PDF files or substantial reproductions of political party programmes.
   - The platform **MUST** provide direct outbound HTTPS links pointing to the party's official publication URL or official direct PDF link.
4. **Official Acts and Public Decrees (Art. 13 TRLPI):**
   - Official election decrees (e.g. Royal Decrees dissolving Cortes and calling elections) and JEC proclamations published in the *Boletín Oficial del Estado* (BOE) are excluded from intellectual property protection under Article 13 TRLPI.

#### Source Rights Taxonomy

Every source registered in the source register (`content/sources/register.json`) is assigned one of five explicit rights review statuses:

| Status | Permitted Use | Build Rule |
|---|---|---|
| `link_and_short_quote` | Outbound links and short verbatim quotes within statutory limits (<= 40 words). | Verbatim quotes permitted if verified and dual-reviewed. |
| `public_domain` | Outbound links and quotes from public-domain or CC0-licensed documents. | Verbatim quotes permitted if verified and dual-reviewed. |
| `link_only` | Outbound links to official document; **NO** verbatim quotation permitted. | Build rejects any verbatim quotation referencing this source. |
| `permission_denied` | Rights holder explicitly objected or restricted usage. | Build rejects any quotation and requires editorial review of linking. |
| `not_reviewed` | Rights status analysis pending. | Build rejects any extracted quotation referencing this source. |

---

### 6.2 Verbatim Quotation Limits and Unsupported Quote Prohibition

The platform prioritizes neutral, objective summaries drafted by the editorial team. Verbatim quotations serve exclusively as supporting evidence for specific technical commitments, figures, regulatory mechanisms, or distinctive phrases.

#### Quantitative and Qualitative Quotation Limits

1. **Maximum Word and Character Ceiling:**
   - A verbatim quote **MUST NOT** exceed **40 words**.
   - A verbatim quote **MUST NOT** exceed **300 characters** (including whitespace).
2. **Mandatory Citation Coordinates:**
   - Every quotation **MUST** cite an exact locator within the official document: either `page` (e.g. `112`), `section` (e.g. `Medida 84`), or both.
   - General citations (e.g. "Programa general" without page/section) are strictly prohibited for verbatim quotes.
3. **Operative Substance Rule:**
   - Verbatim quotations must extract strictly operative policy commitments (target numbers, dates, fiscal percentages, administrative bodies, statutory thresholds).
   - Quotations must **NOT** extract rhetorical flourishes, party slogans, personal attacks, ideological preambles, or electoral appeals.
4. **Typographical Delimitation:**
   - Verbatim quotes must be clearly set off with quotation marks (`«...»` or `"..."`) in the summary or qualification text.
5. **Unsupported Quote Prohibition:**
   - **NO UNSUPPORTED QUOTE CAN PASS REVIEW.**
   - An extracted quote is considered unsupported and **MUST FAIL** automated build validation if:
     1. It lacks verified source coordinates (`page` or `section`).
     2. The referenced source document does not exist in the verified source register.
     3. The referenced source is not in `verified` status (e.g. `missing`, `announced`, `partial`, or `published-unverified`).
     4. The source rights review status is `not_reviewed`, `link_only`, or `permission_denied`.
     5. The quote text exceeds 40 words or 300 characters.
     6. The statement lacks approval from two distinct human reviewers.

---

### 6.3 Editorial Reviewer Roles and Segregation of Duties

To eliminate individual bias, human error, and arbitrary classifications, the editorial team operates under the **Four-Eyes Principle** (Dual Review) with strict segregation of duties.

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Drafter / Extractor                                      │
│    - Extracts candidate proposal & short operative quote    │
│    - Records page/section locator                           │
│    - Drafts neutral Spanish summary                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Editorial Reviewer 1 (Factual and Citation Auditor)      │
│    - Checks quote against original PDF page/section         │
│    - Enforces <= 40 word / <= 300 char limits               │
│    - Verifies source rights status (link_and_short_quote)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Editorial Reviewer 2 (Neutrality and Balance Auditor)    │
│    - Checks neutral phrasing (no evaluative adjectives)     │
│    - Verifies taxonomy classification (Section 5)           │
│    - Verifies absence != opposition                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                  ┌────────────┴────────────┐
             All Agree                 Dispute
                  │                         │
                  ▼                         ▼
┌───────────────────────────┐ ┌───────────────────────────────┐
│ Publication Approved      │ │ 4. Lead Editor Dispute        │
│ Dual-review record signed │ │    Resolution & G0/G2 Signoff │
└───────────────────────────┘ └───────────────────────────────┘
```

#### Reviewer Roles

1. **Drafter / Extractor (`drafter`):**
   - Extracts policy proposals from registered, verified programmes.
   - Extracts short verbatim quotes (<= 40 words) and records exact page/section locators.
   - Drafts the objective Spanish summary (`summary_es`) using factual, non-evaluative verbs.
   - Assigns provisional topic and subtopic according to the Section 5 taxonomy.
   - Note: May be a human researcher or an assistive extraction script. A drafter **CANNOT** approve their own extraction as a reviewer.
2. **Editorial Reviewer 1 (`editorial_reviewer_1` - Factual and Citation Auditor):**
   - Inspects the original document PDF at the exact page/section coordinates.
   - Verifies quote fidelity against the original source text.
   - Verifies that quotation limits (<= 40 words, <= 300 chars) are respected.
   - Verifies that source rights permit quotation (`link_and_short_quote` or `public_domain`).
   - Verifies single-proposal granularity (one discrete policy per record).
3. **Editorial Reviewer 2 (`editorial_reviewer_2` - Neutrality and Balance Auditor):**
   - Independent second reviewer.
   - Verifies that the summary uses strictly descriptive, objective, non-partisan language without praise or condemnation.
   - Confirms correct primary operational topic and subtopic alignment.
   - Verifies that lack of proposal coverage is recorded as `not_found`, never conflated with active opposition.
   - Verifies conditions and qualifications are accurately represented.
4. **Lead Editor (`lead_editor` - Dispute Resolver and Signoff Gatekeeper):**
   - Resolves formal disagreements between Reviewer 1 and Reviewer 2.
   - Authorizes and signs off on correction records.
   - Represents the editorial team for human release gates G0 and G2.

#### Segregation Rules and Impartiality Code

1. **Four-Eyes Principle:** Every published position requires explicit, recorded approval by at least two distinct human reviewers (`reviewed_by_1 != reviewed_by_2`).
2. **Separation of Drafter and Second Reviewer:** A drafter may act as Reviewer 1 if human capacity requires, but **CANNOT** act as Reviewer 2 (`drafter != reviewed_by_2`).
3. **Conflict of Interest Policy:**
   - All reviewers must disclose any formal political party affiliation, candidacy, or campaign advisory role.
   - A reviewer with an active affiliation to a political party is strictly disqualified from reviewing statements or proposals associated with that party or its direct electoral competitors in the same constituency.

---

## 7. Internal Correction Process and Invalidation Protocol

Errors in transcription, page citation, topic classification, or source replacement must be resolved swiftly through a disciplined, transparent, and auditable process.

---

### 7.1 Correction Triggers and Severity Levels

Corrections are initiated via three channels:
1. **Internal Audit:** Discrepancies identified during routine editorial checks or comparison authoring.
2. **Source Replacement:** Political party releases an errata sheet or superseded programme version (`replaced` status).
3. **External Notice:** Inquiries submitted to the project editorial contact (`editorial@elecciones2026.es`).

#### Severity Classification and SLA Targets

| Severity | Definition | Examples | Response / Triage SLA | Publication SLA |
|---|---|---|---|---|
| **Critical (Sev-1)** | Factual inversion, misattributed quote, copyright breach, or non-existent proposal. | Statement claims party supports a tax hike when programme promises a tax cut; quote from unverified document. | **<= 4 hours** (immediate public quarantine) | **<= 12 hours** |
| **Major (Sev-2)** | Substantive inaccuracy in proposal mechanism, incorrect page/section locator, or primary topic misclassification. | Page cited is 44 instead of 144; measure classifies rental assistance under tax instead of housing. | **<= 12 hours** | **<= 24 hours** |
| **Minor (Sev-3)** | Typographical error in summary, punctuation fix, or subtopic refinement without altering comparison meaning. | Minor spelling error in Spanish summary; refined subtopic classification. | **<= 24 hours** | **<= 48 hours** |

---

### 7.2 Immutable Versioning and Correction Records

1. **Immutability of Identifiers:** Published statement IDs (`id`, e.g. `stmt-pp-housing-001`) are immutable. They are never deleted or silently overwritten.
2. **Correction Record Structure:**
   Every substantive edit generates an immutable, dated `CorrectionRecord`:
   - `id`: Unique identifier (e.g. `corr-2026-001`).
   - `statement_id`: Affected statement identifier.
   - `election_id`: Target election (e.g. `es-gen-2026`).
   - `date`: Date of correction (YYYY-MM-DD).
   - `correction_type`: One of `factual_error`, `classification_error`, or `source_replacement`.
   - `severity`: One of `critical`, `major`, or `minor`.
   - `prior_value`: Exact previous text, quote, or classification.
   - `new_value`: Corrected text, quote, or classification.
   - `reason`: Concise public explanation of the correction rationale.
   - `reviewed_by`: Identifier of the auditing reviewer.
   - `approved_by`: Lead Editor signoff.

---

### 7.3 Automatic Invalidation of Dependent Comparison Relationships

A policy comparison (`ComparisonRelationship`) depends directly on the integrity of the underlying party statements.

#### Invalidation Rules

1. When a statement is corrected or marked `invalidated`, the static build pipeline **MUST AUTOMATICALLY INVALIDATE** all comparison records that reference that statement ID.
2. An invalidated comparison is assigned `status: "invalidated"` and receives a documented `invalidation_reason`.
3. Invalidated comparisons **MUST NOT** be rendered in the public comparative views until two editorial reviewers re-evaluate the comparative relationship and record fresh approval.
4. When a programme version is marked `replaced`, all derived comparison relationships are flagged for mandatory re-review against the successor document.

---

### 7.4 Public Errata Log and Transparency

1. The public site publishes an authoritative, chronological errata log at `/correcciones/` and summarized on the methodology page.
2. Each errata entry discloses the affected party, topic, date, prior text, corrected text, and explanation.
3. Factual corrections are acknowledged transparently without concealing editorial revisions.
