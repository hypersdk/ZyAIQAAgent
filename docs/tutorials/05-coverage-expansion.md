# Tutorial 5 — Coverage Expansion

Let the agent discover what your test suite is missing: it reads the product repo's code and docs (and optionally crawls the live site), compares what it finds against your existing tests, and generates tests for the gaps.

**Prerequisites:** [Tutorial 4](04-github-integration.md) — GitHub auth and `ZYVOR_PRODUCT_REPO` configured.

---

## 1. Discover only (no generation)

Start with a dry look at the inventory:

```bash
argus test discover --source github
```

```
Discovered 47 coverage candidate(s)
Uncovered gaps: 12
Files scanned: 63
  [gap] route /gpu-passthrough — Gpu Passthrough
  [gap] route /case-studies — Case Studies
  [gap] page /integrations — Integrations
  ...
```

What it scanned (defaults, configurable via `COVERAGE_DISCOVERY_PATHS`):

| Repo location | Candidates extracted |
|---------------|---------------------|
| `src/pages/`, `src/routes/`, `app/` | Route files → route candidates (`src/pages/vm.tsx` → `/vm`) |
| `docs/`, `docs/specs/`, `README.md`, `CHANGELOG.md` | Markdown headings → page/doc candidates |
| `sidebars*.js/ts`, `docusaurus.config.*` | Sidebar doc IDs |
| `openapi*.json/yaml` | API path candidates |

A candidate counts as **covered** when its path or slug appears in any existing spec — in a `goto()` call, a `toHaveURL` pattern, or a test title.

## 2. Generate tests for the gaps

```bash
argus test run --source github --expand-coverage
# or generation only:
argus test generate --source github --expand-coverage
```

Each gap becomes a requirement (`navigate → wait → assert heading/content`) and then a spec file:

```
tests/generated/coverage-route-gpu-passthrough-….spec.ts
```

New tests per run are capped by `COVERAGE_MAX_NEW_TESTS` (default 10) — highest-priority gaps first — so a big repo doesn't flood your suite. Run again to work through the backlog; already-covered candidates drop out each time.

To make expansion the default for all GitHub runs (including webhook events), set in `.env`:

```bash
ENABLE_COVERAGE_EXPANSION=true
```

Note: passing an explicit `--spec` disables expansion unless you also pass `--expand-coverage`.

## 3. PR-scoped discovery

On webhook `pull_request`/`push` events (or `discover --pr-number N`), discovery is scoped to the **changed files** — so a PR that adds `src/pages/pricing.tsx` gets exactly one new gap: `/pricing`. The PR comment then includes a Coverage section:

```
### Coverage
- Inventory: 3 candidate(s)
- Gaps remaining: 1
- New coverage tests generated: 1
```

## 4. Add live-site crawling

Code/docs discovery only sees what's in the repo. To also discover what's actually deployed:

```bash
# .env
ENABLE_LIVE_CRAWL=true
CRAWL_MAX_PAGES=50
CRAWL_MAX_DEPTH=2
```

During `discover`, a headless Chromium BFS-crawls same-origin links from `/`, and crawled routes merge into the inventory. You can also run it standalone:

```bash
npm run crawl
cat reports/crawl-inventory.json
```

## 5. Measure JS coverage of your runs

To see how much of the site's JavaScript your tests actually exercise:

```bash
# .env
ENABLE_V8_COVERAGE=true

argus test exec
```

Each test writes V8 coverage to `reports/v8-coverage/`, aggregated into the HTML report and PR comment as a percentage. Low-coverage files hint at untested interactive features.

## 6. Tuning

| Variable | Default | When to change |
|----------|---------|----------------|
| `COVERAGE_DISCOVERY_PATHS` | `docs/, docs/specs/, CHANGELOG.md, README.md, src/pages/, src/routes/, app/` | Your repo uses different layout (e.g. `apps/web/pages/`) |
| `COVERAGE_MAX_NEW_TESTS` | 10 | Raise for an initial backfill, lower for steady state |
| `COVERAGE_MAX_DISCOVERY_FILES` / `_BYTES` | 200 / 2 MB | Large monorepos |

### Regenerating after quality improvements

Generated coverage stubs from older pipeline versions can be refreshed:

```bash
rm tests/generated/coverage-*.spec.ts
argus test generate --source github --expand-coverage
```

**Next:** [Tutorial 6 — Visual regression](06-visual-regression.md).
