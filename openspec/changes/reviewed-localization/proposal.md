# Proposal: Reviewed localization

## Why

The Spanish MVP serves the whole Spanish audience. Later language options may improve access, but inaccurate translations of political statements can change their meaning.

## What Changes

- Separate public interface strings from code and version them by locale.
- Add Catalan as the first reviewed translation, including method, source labels, and corrections.
- Consider English only after demand and editorial capacity are confirmed.
- Keep original programme wording and identify translated summaries as translations.
- Require bilingual editorial review for political claims and language-specific accessibility checks.

## Capabilities

### New Capabilities

- `locale-content`: Publish reviewed translated interface and editorial text.

### Modified Capabilities

- `static-publication`: Generate locale routes, canonical language links, and consistent source references.

## Impact

This is **phase 5 or later**. It does not change the Spanish MVP release gate. English remains optional, not a committed release. Detailed specs, design, and tasks must follow a real editorial staffing decision.
