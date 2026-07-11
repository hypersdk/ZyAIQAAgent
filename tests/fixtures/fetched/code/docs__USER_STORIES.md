# hypersdk-web User Stories

**Product:** HyperSDK platform marketing and documentation website

Cross-reference: [Documentation index](README.md) · `README.md` (repo root)

## Personas

| Persona | Name | Focus |
|---------|------|-------|
| Marketing | Alex | Publish product pages and blog posts |
| Sales | Morgan | ROI calculator and lead capture |
| Docs Contributor | Jordan | Edit Docusaurus content |

---

### Story 1 — Run local dev site

**As Jordan** (Docs Contributor), I want preview marketing pages at localhost:3000, **so that** I deliver reliable outcomes.

| Criterion | Notes |
|-----------|-------|
| Core capability | npm start, Docusaurus 3 |

---

### Story 2 — Capture leads

**As Morgan** (Sales), I want whitepaper download with utm attribution, **so that** I deliver reliable outcomes.

| Criterion | Notes |
|-----------|-------|
| Core capability | contact form, session storage UTMs |

---

### Story 3 — Build production

**As Alex** (Marketing), I want deploy static site with analytics, **so that** I deliver reliable outcomes.

| Criterion | Notes |
|-----------|-------|
| Core capability | npm run build, PLAUSIBLE_DOMAIN |

---

## Validation

Map each story to smoke tests, CI jobs, or manual lab steps before marking production-ready.
