# Design: Programme alignment quiz

## Context

Roadmap package: **E4.1**, planning for **G5**. See `proposal.md` for motivation and the four delta specs for behavior. This design is a proposal for review. Numerical limits below are proposed product rules, not evidence of statistical validity or recorded editorial approval.

The repository has a Python reviewed-data generator, provenance and correction records, an eight-topic taxonomy, static Spanish pages, local scripts, and Docker/Nginx serving. It has no quiz engine or reviewed quiz set. The main OpenSpec inventory is empty; the MVP change is not archived. Preserve its provenance, deterministic build, election isolation, and publication constraints.

`docs/CONTENT-METHODOLOGY.md` prohibits party ranking. Use alphabetical result cards, without a leaderboard. `docs/SECURITY.md` permits retained technical connection logs. The quiz's stricter zero-tracking contract requires a reviewed operational reconciliation before release. Do not silently claim that the existing deployment meets it.

## Goals / Non-Goals

**Goals:** a fixed auditable measurement contract; identical comparison denominators; traceable source mappings; local and inspectable arithmetic; accessible states; enforceable privacy boundaries.

**Non-Goals:** an ideological model, electoral advice, prediction, server computation, answer recovery, personalized sharing, adaptive questions, or automatic approval of political content. This change creates no programme records or political questions.

## Decisions

### 1. Static reviewed bundle with immutable versions

Extend the offline Python build in E4.2. Publish one content-addressed quiz bundle with the static page and local script. Load the complete bundle once, before accepting answers. All answer and result states stay within the same document; do not fetch party-specific details on demand. This makes request patterns independent of political answers. A dynamic API would add data-transfer risk and operational cost without serving this flow.

The bundle contains these public contracts:

| Record | Required fields |
|---|---|
| Set | election ID, set ID/version, taxonomy version, method version, bundle hash, publication/review dates, fixed ordered item IDs, inclusion-policy reference |
| Item | stable item and measure IDs, primary topic, Spanish text, qualifications, response labels, source statement references, approval state |
| Party mapping | party ID, item ID, `support`/`reject`/gap status, numeric value only for supported mappings, statement and programme references, exact locator, review evidence reference |
| Source | official URL, programme ID/version/hash, source and rights status, retrieval date, review date, correction references |
| Coverage | every included party and item, eligibility, reason for every gap, territorial scope from approved register |

Keep reviewer evidence and conflict disclosures in the editorial record. Publish only approved review metadata, not private reviewer information. Escape source strings as text. Validate official source URLs and prohibit executable or unsafe schemes. Do not include raw PDF/OCR files, credentials, or editorial drafts in public output.

Build checks reject duplicate items, cross-election links, mixed versions, missing sources, invalid approvals, stale correction dependencies, and invalid mapping values. The bundle is immutable for a session. An updated set requires a fresh empty session; no migration of answers between versions.

### 2. Sixteen fixed items with common coverage

Use two items in each of the eight core topics, in taxonomy order, then stable item-ID order within a topic. Two items per topic is a reviewable starting scope that covers all topics while limiting mobile length. More items or adaptive sampling would change the contract and need a spec revision.

Select from specific approved programme measures. Editors record the objective, instrument, conditions, competence, and selection/rejection rationale. Avoid repeating one measure under several topics or disproportionately deriving items from one party's wording. Do not name a party in the response prompt. Make party/source attribution inspectable in a separate, equally structured disclosure before and after answering.

Require full 16-item mapping coverage for every scored party and at least two eligible parties. Keep all other included parties visible with explicit gaps. Per-party denominators would let a party with sparse evidence appear more aligned than a fully documented party; imputation would invent positions. The stricter common-coverage rule can prevent launch. That is preferable to an unsupported comparison, but editors must audit exclusion patterns and can reject the set as biased. A future lower-coverage method requires a reviewed spec revision.

Only complete, verified official target-election programmes support numeric scores. A partial programme can appear in coverage with reviewed source details but cannot qualify as complete scoring coverage. Programme silence never means rejection. Conditional measures qualify only if the item retains all relevant conditions and reviewers can support the same binary interpretation for all scored parties. Otherwise reject the item or record a gap.

### 3. Deterministic arithmetic and answer thresholds

Draft answer labels and values are:

| Spanish UI draft | Value |
|---|---:|
| Totalmente en desacuerdo | -1 |
| Más bien en desacuerdo | -0.5 |
| Ni de acuerdo ni en desacuerdo | 0 |
| Más bien de acuerdo | 0.5 |
| Totalmente de acuerdo | 1 |
| No lo sé / Omitir | absent |

Party positions are -1 (explicit rejection) or 1 (explicit support). Do not infer intensity, neutrality, opposition from silence, or a position from general ideology. An intermediate visitor answer is a defined scale response; it is not an inferred party position.

For eligible party `p`, answered item `i`, and topic `t`:

```
m[p,i] = 1 - abs(a[i] - b[p,i]) / 2
n[t] = number of numeric answers in topic t
M[p,t] = sum(m[p,i] for answered i in t) / n[t]
T = topics with n[t] > 0
S[p] = 100 * sum(w[t] * M[p,t] for t in T) / sum(w[t] for t in T)
```

Default weights are 1. A visitor can locally choose 2 for a topic through “Dar más peso a este tema”. Offer “Restablecer pesos”. Apply the same weights to every eligible party. Do not allow hidden party weights or zero-weight exclusions. Topics without answers are omitted from `S`, visibly disclosed, and retained in the full-set bounds below.

Display aggregates only with at least eight numeric answers across four topics. These are conservative disclosure limits for a short quiz, not a validated confidence threshold. An explicit zero is an answer; skip and unknown are absent. Revising a response replaces its contribution. Clearing a response removes it and can cause the aggregate to become unavailable.

Because permitted item alignments are quarters and weights are small integers, use integer quarter units and rational cross-products for exact aggregate comparisons. Display round-half-up integer percentages; never round intermediate means. This prevents floating-point artifacts from breaking exact ties. Sort by Spanish display name with stable party ID as a fallback, never by score. Mention exact ties and differences of at most one unrounded point; explain equal rounded values separately.

### 4. Bounds and sensitivity without statistical claims

For each topic, retain fixed contributions from answered items. Each skipped item's permitted alignment ranges from 0 to 1. There are always two items in a topic. Full-set bounds are:

```
L[p,t] = sum(answered m[p,i] in t) / 2
U[p,t] = (sum(answered m[p,i] in t) + skipped_count[t]) / 2
L[p] = 100 * sum(w[t] * L[p,t] over all 8 topics) / sum(w[t] over all 8 topics)
U[p] = 100 * sum(w[t] * U[p,t] over all 8 topics) / sum(w[t] over all 8 topics)
```

These are feasible per-party extrema over permitted skipped responses. They are not a joint ordering guarantee across parties. With no skips they collapse to `S`. With skips they describe the completed-set calculation, whose denominator differs from the answered score; explain this explicitly rather than implying that `S` must lie inside those bounds. If two parties' bounds overlap, state that the unanswered items can affect their relative alignment. Do not call any interval a confidence interval.

For sensitivity, remove each answered item in turn and recompute `S` only when the remaining answers satisfy the minimum threshold. Show the min/max of valid recomputations, the number tested, and which removal changes the score most. If none qualify, show an unavailable explanation. Treat each removal as a hypothetical calculation; do not alter the visitor's saved-in-memory answers.

Plain Spanish drafts: “El porcentaje resume solo las medidas que has respondido”; “Si respondieras las preguntas omitidas, el cálculo completo podría cambiar”; “Este intervalo muestra escenarios posibles, no una probabilidad”; “No hay datos suficientes para calcular un porcentaje”. Final copy needs human review.

### 5. Phone flow with inspectable explanations

Use one static `/cuestionario/` entry. Keep introduction → question → results as in-memory states, with optional answer review accessible from questions and results. Include method and citation disclosures within the page, so inspection does not destroy answers. Open official source links in a clearly indicated new context with `noopener noreferrer`. Warn that navigating away or refreshing loses the session.

The question state shows topic, “Pregunta N de 16”, response group, source disclosure, previous, next, and skip. Selecting a radio does not advance. The optional answer review shows all 16 items with answer/skip/unvisited state and an edit control. The question state explains that unfinished items count as skipped. Selecting “Ver resultado” converts unfinished items to skips and opens results directly; review is never required. The final question also opens results when explicitly skipped. Results show alphabetically ordered cards, answered-topic coverage, source gaps, weights, whole-number alignment, bounds, and sensitivity.

“Cómo se calcula” exposes current answer and mapped position, item arithmetic, topic mean, normalized topic weight, aggregate contribution, and exact source. Keep the immediately previous aggregate in memory only to explain an edit. Every control and source link has a 44-by-44-CSS-px target. Prefer semantic controls and stacked details over a chart or horizontally scrolling matrix. A chart, if added, must have equivalent text.

Show visitor answer labels and support/rejection words in item details, with the item text and agreement percentage. Explain a normalized topic weight as its share of the current calculation, and state whether an aggregate rose, fell, or stayed unchanged. When all 16 items are answered, explain that the full-set limits equal the current percentage instead of suggesting that skipped items remain. The formula stays available in the method disclosure. The local copy is a draft; use `docs/QUIZ-COMPREHENSION.md` for voluntary human checks without collecting political preferences.

Resetting topic weights is an in-place result update, not navigation to a new
state. Rebuild the results without heading focus, reopen the weight disclosure,
and focus the replacement reset button by its stable control ID. Use the
existing polite status to confirm normal weights. Preserve answers and the
previous aggregate for the existing change explanation. The control ID contains
no answer or score. Test forward/reverse keyboard navigation, focus visibility,
and unchanged answer coverage with fictional fixtures at 360/390/430 CSS px;
this does not replace manual screen-reader or real-device acceptance.

The complete flow must pass the [WCAG 2.2 A/AA conformance requirements](https://www.w3.org/TR/WCAG22/#conformance-reqs). Maintain a criterion audit covering all pages and states, including errors, no-script and unavailable-set states. Test 360/390/430 px, reflow at 320 CSS px, orientation, zoom, text spacing, keyboard, VoiceOver/Safari, and NVDA/Firefox. Verify text/control contrast, labels, reading order, status messages, pointer cancellation, and focus not obscured. Do not claim compliance from automated tests or these artifacts alone.

### 6. Memory boundary and zero tracking

Keep answers, progress, weights, results, and prior aggregate values in a page-local state object. Do not write browser storage, history state, URL query/fragment, DOM attributes used by instrumentation, console output, or remote error reports. Clear state on explicit reset, page exit, and restoration from the back/forward cache. Internal question navigation does not leave the document. Browser-managed screenshots or device memory outside application control are not an application persistence mechanism; do not promise forensic erasure.

Bundle all public source/method details before interaction. Answering, skipping, revising, weighting, and scoring require zero network requests. Share only the generic canonical URL. Serve assets locally with a restrictive CSP and a no-referrer policy. No third-party embeds, telemetry, service worker, browser permission, or account feature is needed. A server engine and persistent local storage would conflict with the privacy contract.

The current server CSP permits same-origin connections and the security plan allows technical logs. E4.4 must inspect the actual edge, origin, and monitoring configuration; neither setting proves compliance. Before G5, require no retained visitor-level logs or tracking cookies for quiz delivery, including CDN facilities and error systems. Aggregate health metrics must be free of visitor identifiers. Document unavoidable transient connection processing honestly. If the provider cannot meet this contract, do not release the quiz through it until an approved compliant delivery path exists. External official-source sites are outside project control; disclose that boundary and send no referrer.

### 7. Fairness audit protocol

Keep a versioned editorial register of candidates, selected/rejected measures, provenance, coverage reasons, reviewer disagreements, and resolutions. Two distinct human reviewers approve each item and mapping under the existing editorial conflict policy. A separate review lane checks selection and score presentation. This planning task records no approval identities or verdicts.

Audit all eight topic quotas, duplicated concepts, wording polarity, complexity, preserved conditions, common denominator, unscored parties, and how much selected wording derives from each party's source. Equal quotas do not prove fairness. Test that permuting party IDs or display order leaves calculations unchanged; use fictional abstract IDs and numeric fixtures without invented political text. Test reverse answer/position polarity for invariant alignment, ties, gaps, skip patterns, and weight changes.

For voluntary comprehension tests, use fictional answer assignments rather than participant political preferences. Each participant must locate a citation, explain an answer edit, distinguish skip/neutral/missing evidence, and recognize the non-recommendation and bounds wording. Record aggregate completion outcomes only. A misunderstood limit requires revised copy and a retest before G5. No political answer recording or session replay is allowed.

## Risks / Trade-offs

- [Complete coverage prevents launch or excludes parties] → show all gaps; audit exclusion patterns; keep the quiz unavailable if coverage or fairness fails.
- [Binary party mappings flatten conditions] → require exact scoped measures; reject mappings that cannot preserve relevant conditions.
- [Percentages imply electoral advice or precision] → whole-number display, alphabetical cards, visible denominators and limits, explicit non-recommendation.
- [Topic normalization surprises users after skips] → expose means and active topics; distinguish answered scores from full-set bounds.
- [Reset on exit frustrates visitors] → state the boundary before entry; keep method and review inside the document.
- [Infrastructure logs conflict with strict privacy] → require configuration evidence and policy reconciliation before G5.
- [Historical or corrected content reaches a current result] → election isolation, immutable bundle versions, fail-closed validation, and corrected rollback checks.
- [Accessible-looking screens fail the complete process] → criterion audit plus manual phone, keyboard, and assistive-technology review.

## Migration Plan

1. The user authorized local technical implementation with mock data before G4/E1.4. Keep that preview opt-in, clearly fictional, and non-indexable. Obtain review of E4.1 and recorded G4/E1.4 prerequisites before real content activation. Real item selection also needs the applicable G0 rights and editorial approvals.
2. Build a private preview from clearly fictional numeric fixtures. Add the approved real set only after dual review and the fairness audit. Generate the same static artifact twice and compare hashes.
3. Run E4.3 and E4.4 checks in the local Docker preview and representative delivery configuration. Benchmark static delivery on the existing 2-vCPU/8-GB scenario and record mobile load behavior. Require all G5 evidence before public activation.
4. Release only by the existing approved immutable-artifact process. Retain the prior verified artifact. On a functional regression restore it only if its source rights, citations, and correction status remain valid.
5. For a source or rights defect, disable the quiz route with a Spanish explanation and retain method/correction information. Do not roll back to a withdrawn or invalidated question set. Re-enable only after a corrected bundle and fresh review.

## Review status

Technical documents use controlled English principles. No qualified ASD-STE100 review or accessibility conformance audit has been completed by writing this design. The human review must approve the 16-item scope, strict coverage rule, scale, weights, and answer thresholds as one coherent E4.1 contract. Changing these rules requires corresponding spec and task updates before implementation.
