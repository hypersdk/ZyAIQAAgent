# Zyvor QA Agent

[![ZyAIQAAgent Mission Control — Full KT Walkthrough](https://i.ytimg.com/vi/-_2jph4jW7c/maxresdefault.jpg)](https://youtu.be/-_2jph4jW7c)

**Full KT walkthrough (YouTube):** sign-in → status hero & pod fleet → the 20+ capability Actions panel → a live Smoke test run → a Flow test result → a Site audit grade → network & security probes → Ask Zyvor Q&A → NOC wall mode — [watch](https://youtu.be/-_2jph4jW7c)

## 🎬 More recordings

<table>
<tr>
<td width="50%" align="center">
<a href="https://youtu.be/ys7SvKKqf9w">
<img src="https://i.ytimg.com/vi/ys7SvKKqf9w/maxresdefault.jpg" alt="Mission Control → GuestKit flow demo" width="100%">
</a>
<br><b>Mission Control → GuestKit flow</b><br>
<sub>Login → enter a GuestKit URL → run journey — <a href="docs/tutorials/13-test-zyvor-dev-recording.md">how-to</a></sub>
</td>
<td width="50%" align="center">
<a href="https://youtu.be/oXVVWZiRgQY">
<img src="https://i.ytimg.com/vi/oXVVWZiRgQY/maxresdefault.jpg" alt="Autonomous Playwright journey against zyvor.dev" width="100%">
</a>
<br><b>Autonomous journey vs zyvor.dev</b><br>
<sub>Steps file: <a href="docs/assets/zyvor-dev-demo.steps">zyvor-dev-demo.steps</a></sub>
</td>
</tr>
<tr>
<td width="50%" align="center">
<a href="https://youtu.be/EwqVdjSabvE">
<img src="https://i.ytimg.com/vi/EwqVdjSabvE/maxresdefault.jpg" alt="Direct browser journey of the GuestKit GitHub README" width="100%">
</a>
<br><b>GuestKit GitHub README journey</b><br>
<sub>Direct browser journey, no dashboard</sub>
</td>
<td width="50%" align="center">
<a href="https://youtu.be/43pSPf-FVsE">
<img src="https://i.ytimg.com/vi/43pSPf-FVsE/maxresdefault.jpg" alt="Direct journey of zyvor.dev/guestkit" width="100%">
</a>
<br><b>zyvor.dev/guestkit journey</b><br>
<sub>Direct journey of the GuestKit product page</sub>
</td>
</tr>
</table>

```bash
zyvor-qa flow https://zyvor.dev --steps docs/assets/zyvor-dev-demo.steps --video
```

## 📖 Feature Guide

**[Wiki](https://github.com/hypersdk/ZyAIQAAgent/wiki)** — operator cheat sheets (CLI, Mission Control, journeys, CI/CD, deploy).

**[Zyvor QA Agent — Customer Feature Guide](docs/zyvor-qa-agent-customer-feature-guide.md)** — a complete, customer-facing reference covering **Mission Control**, journeys, probes, and optional **Ask Zyvor** knowledge Q&A. Also available as a print-ready **[PDF](docs/zyvor-qa-agent-customer-feature-guide.pdf)**.

Autonomous AI testing agent for [Zyvor](https://zyvor.dev) — an AI-first infrastructure platform. Continuously validates the Zyvor platform by reading requirements from GitHub, generating Playwright tests, executing them after deployments, detecting regressions, and producing actionable reports.

Ships with **Mission Control** — a live web console (`zyvor-qa serve` → `/dashboard`) that runs 20+ QA capabilities on demand with streamed output and CSV/HTML/PDF reports: the full test pipeline, **E2E flow tests** (multi-step journey → one video + Playwright trace, cross-browser/device/throttle), **HAR record / replay**, **Playwright codegen import**, **API contract tests** (OpenAPI schema validation + multi-step workflows), **auth & session** tests (reusable login), **live-data** tests (WebSocket/SSE assertions), **Core Web Vitals**, **route sweeps** (visual diff at desktop/mobile), site audits (a11y/SEO/perf/security with an A–F grade), ten network & security probes, load and TLS checks, flaky detection, screenshots, and recurring monitors. Optionally enable **Ask Zyvor** — a citation-first LangChain knowledge agent (Qdrant hybrid retrieval) for product docs Q&A inside the same console ([Tutorial 14](docs/tutorials/14-ask-zyvor-knowledge.md)). See [`docs/tutorials/10-mission-control-dashboard.md`](docs/tutorials/10-mission-control-dashboard.md), [`11-flow-tests.md`](docs/tutorials/11-flow-tests.md), and [`12-api-auth-realtime.md`](docs/tutorials/12-api-auth-realtime.md).

### Mission Control UX

The console is a full-bleed ops surface (glass sticky topbar/footer, larger type, primary **Smoke** CTA, card motion) with a short **boot splash**, a live **signal-field / constellation** canvas, **⌘K** command palette, **NOC wall mode** (double-click the brand), and light **warp** cues (`` ` `` or type `zyvor`). Reduced-motion preferences are respected.

## Architecture

```
GitHub (specs, PRs, deploy events)
        │
        ▼
LangGraph Orchestrator (Python)
        │
   fetch → parse → generate → execute → regression → api_validate → log_analyze
        │
   ┌────┴──── pass → report → notify
   └──── fail → analyze → autofix → report → notify
        │
   Playwright (Node.js) + Rust diff (optional)
```

- **Orchestrator**: LangGraph state machine coordinates all pipeline stages
- **AI agents**: LLM-provider agnostic via LangChain (OpenAI, Anthropic, Azure, Google, Ollama)
- **Test execution**: Playwright (TypeScript) with screenshot, video, trace capture
- **Cursor**: development assistant only — not a runtime dependency

## Quick Start

### Container (v0.4.0)

```bash
docker pull ghcr.io/hypersdk/zyaiqaagent:v0.4.0
# or
docker pull ghcr.io/hypersdk/zyaiqaagent:latest

docker run --rm --env-file .env ghcr.io/hypersdk/zyaiqaagent:v0.4.0 test --grep @smoke
docker run --rm -p 8080:8080 --env-file .env ghcr.io/hypersdk/zyaiqaagent:v0.4.0 serve --port 8080 --host 0.0.0.0
```

Release notes: [v0.4.0](https://github.com/hypersdk/ZyAIQAAgent/releases/tag/v0.4.0) · full pull/run guide: [docs/releases.md](docs/releases.md)

### Prerequisites

- Python 3.10+ (3.11+ recommended)
- Node.js 20+
- Git

### Install

```bash
cp .env.example .env
make install
```

### Run smoke tests (no LLM required)

```bash
zyvor-qa test --grep @smoke
```

Against the public demo site (video + HAR): [Tutorial 13](docs/tutorials/13-test-zyvor-dev-recording.md).

### Run full pipeline from GitHub (your product repo)

```bash
# Ensure .env has ZYVOR_PRODUCT_REPO=ssahani/hypersdk-web
gh auth login

# Generate + run tests from a specific markdown file in the repo
zyvor-qa run --source github --spec docs/specs/my-feature.md

# Generate tests only
zyvor-qa generate --source github --spec docs/specs/my-feature.md
```

See [**Writing Tests & GitHub Integration**](docs/test-authoring.md) for the full command reference.

## Documentation

**Operator wiki:** [https://github.com/hypersdk/ZyAIQAAgent/wiki](https://github.com/hypersdk/ZyAIQAAgent/wiki)

**Customer manual (page-by-page Mission Control):** [`docs/customer/`](docs/customer/README.md) — regenerate guides / PDFs / website sync with `scripts/customer-docs/` (same pattern as Zeus OS).

**New here? Start with the [step-by-step tutorials](docs/tutorials/README.md)** — 15 hands-on guides from install to external CI/CD integration.

| Guide | Description |
|-------|-------------|
| [**Customer docs**](docs/customer/README.md) | Mission Control page-by-page manual · PDFs · `sync-to-website.mjs` |
| [**Enterprise v2**](docs/enterprise-v2.md) | Fail-closed security, SSRF allowlists, durable SQLite jobs, `/api/v2`, RBAC |
| [**Tutorials**](docs/tutorials/README.md) | Getting started, spec-to-test, NL tests, GitHub, coverage, regression, autofix, notifications, CI/CD, dashboard, E2E flow tests |
| [**External CI/CD integration**](docs/tutorials/15-external-cicd-integration.md) | Drop zyvor-qa into *any* project's pipeline via the reusable [GitHub Action](action.yml), or GitLab/CircleCI/Jenkins/Azure [templates](templates/ci/README.md) |
| [**Architecture**](docs/architecture.md) | Pipeline internals: LangGraph nodes, state, agents, fallback design |
| [**Configuration**](docs/configuration.md) | Complete environment variable reference with defaults |
| [**Writing Tests & GitHub Integration**](docs/test-authoring.md) | Command reference; manual, spec-driven, and NL test creation |
| [**Mission Control dashboard**](docs/tutorials/10-mission-control-dashboard.md) | The live console: 20+ QA actions, UX cues, audits, probes, schedules, reports |
| [**Test zyvor.dev (recording)**](docs/tutorials/13-test-zyvor-dev-recording.md) | Smoke + flow video + HAR against https://zyvor.dev |
| [**Remote deployment**](docs/remote-deploy.md) | `deploy-remote.sh` — bare host, container, or k3s in one command |
| [**Releases & container image**](docs/releases.md) | GHCR image (`v0.4.0` / `latest`), how to pull it, how to cut a release |
| [**Troubleshooting**](docs/troubleshooting.md) | Common errors and fixes |
| [**Contributing**](CONTRIBUTING.md) | Dev setup, conventions, how to add a pipeline stage |
| [`kubernetes/README.md`](kubernetes/README.md) | Kubernetes deployment |
| [`rust/README.md`](rust/README.md) | Rust `zyvor-diff` screenshot processor |
| [`prompts/examples/vm-create.md`](prompts/examples/vm-create.md) | Example requirement spec |

## CLI Commands

Full examples: [**docs/test-authoring.md**](docs/test-authoring.md)

| Command | Description |
|---------|-------------|
| `zyvor-qa test` | Run hand-written smoke tests only |
| `zyvor-qa run --source local --spec <path>` | Full pipeline from a local markdown spec |
| `zyvor-qa run --source github --spec <path>` | Full pipeline from a GitHub markdown file |
| `zyvor-qa run --source github` | Full pipeline from all GitHub specs/issues |
| `zyvor-qa generate --spec <path>` | Generate tests from local spec (no run) |
| `zyvor-qa generate --source github --spec <path>` | Generate tests from GitHub `.md` (no run) |
| `zyvor-qa discover --source github` | List coverage candidates and gaps (no generation) |
| `zyvor-qa run --source github --expand-coverage` | Pipeline + generate tests for uncovered routes/pages |
| `zyvor-qa create "description"` | Generate tests from plain English |
| `zyvor-qa create "description" --execute` | Generate and run NL tests |
| `zyvor-qa regression` | Visual regression check |
| `zyvor-qa regression --update-baselines` | Capture new screenshot baselines |
| `zyvor-qa flow <url> --steps <file>` | Drive a multi-step journey, recorded as one video + trace |
| `zyvor-qa flow <url> --describe "…"` | Same, from a plain-English journey |
| `zyvor-qa har-replay <url> --mode record\|replay --har <path>` | Capture network as HAR, then drive the UI against it |
| `zyvor-qa import-codegen <file>` | Convert Playwright codegen JS/TS into flow steps |
| `zyvor-qa route-sweep <url> --auto` | Screenshot every crawled route (desktop/mobile), diff vs baselines |
| `zyvor-qa api-test <base> --spec <url>` | Validate REST endpoints against their OpenAPI schema; `--workflow` for multi-step API flows |
| `zyvor-qa auth-test <base> --api-login <path>` | Log in, save a reusable session, assert logout/expiry/negative-auth |
| `zyvor-qa realtime <url> --ws <path>` | Assert WebSocket/SSE streams are live (+ reconnect, live-view) |
| `zyvor-qa vitals <url>` | Core Web Vitals (LCP/CLS/INP) with device + network throttle |
| `zyvor-qa serve` | GitHub webhook server + Mission Control dashboard (`/dashboard`) |
| `zyvor-qa serve --tls` | Serve the dashboard over HTTPS (self-signed) |

## Phase Features

### Phase 2 — Regression, API, Logs

| Feature | Flag | Description |
|---------|------|-------------|
| Screenshot regression | `ENABLE_REGRESSION=true` | Pixel diff against baselines in `screenshots/baselines/` |
| API validation | `ENABLE_API_VALIDATION=true` | Validates HTTP status codes from captured API calls |
| Browser log analysis | always on | Console errors and network failures flagged in report |

```bash
# Capture baselines
make regression-update

# Compare against baselines
make regression
```

### Phase 3 — LLM Analysis & Notifications

| Feature | Flag | Description |
|---------|------|-------------|
| LLM failure analysis | `ENABLE_LLM_ANALYSIS=true` | Root cause + fix suggestions from traces/screenshots |
| LLM report summary | `ENABLE_LLM_REPORT=true` | Plain-English PR comment summary |
| PDF report export | `ENABLE_PDF_REPORT=true` | Generates `reports/qa-summary.pdf` from HTML |
| Slack notifications | `SLACK_WEBHOOK_URL` | Rich block-formatted messages |
| Teams notifications | `TEAMS_WEBHOOK_URL` | Adaptive card messages |
| Email notifications | `SMTP_*` env vars | HTML email with PDF attachment |
| K8s deployment | `kubernetes/` | CronJob, Deployment, Service, Ingress |

```bash
# Deploy to Kubernetes (cluster must be running)
make k8s-validate   # offline manifest check
make k8s-apply      # apply to cluster
```

### Phase 4 — Autofix, NL Tests, Multi-browser, Rust

| Feature | Flag | Description |
|---------|------|-------------|
| Autofix suggestions | `ENABLE_AUTOFIX=true` | LLM-powered selector repair after failures |
| Autofix apply + re-run | `ENABLE_AUTOFIX_APPLY=true` | Patch spec files and re-execute (self-healing) |
| NL test creation | `zyvor-qa create` | Generate tests from plain English |
| Multi-browser | `ENABLE_MULTI_BROWSER=true` | Chromium + Firefox + WebKit |
| Rust diff processor | `ENABLE_RUST_PROCESSOR=true` | Fast screenshot diff via `zyvor-diff` binary |
| Coverage expansion | `ENABLE_COVERAGE_EXPANSION=true` | Discover untested routes/pages from repo code/docs |
| Live site crawl | `ENABLE_LIVE_CRAWL=true` | BFS crawl of the deployed site into coverage inventory |
| V8 JS coverage | `ENABLE_V8_COVERAGE=true` | Measure JS coverage of test runs, reported as % |
| Mission Control dashboard | `zyvor-qa serve` → `/dashboard` | Live K8s pod health, log tails, QA run history + trends |

```bash
# Natural language test
zyvor-qa create "Verify homepage shows all 14 products" --execute

# Build Rust diff tool
make rust

# Multi-browser (manual)
ENABLE_MULTI_BROWSER=true npx playwright test
```

## Environment Variables

See [**docs/configuration.md**](docs/configuration.md) for the complete annotated reference, and [`.env.example`](.env.example) for a starting template. Key variables:

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER` | `openai`, `anthropic`, `azure`, `google`, `ollama` |
| `ENABLE_REGRESSION` | Enable screenshot visual regression |
| `ENABLE_API_VALIDATION` | Enable API response validation |
| `ENABLE_LLM_ANALYSIS` | LLM-powered failure analysis |
| `ENABLE_AUTOFIX` | Selector repair suggestions |
| `ENABLE_MULTI_BROWSER` | Run tests on chromium, firefox, webkit |
| `ENABLE_RUST_PROCESSOR` | Use Rust `zyvor-diff` for screenshot comparison |

## Project Structure

```
├── orchestrator/       # LangGraph pipeline, CLI, webhook
│   └── nodes/          # One node per pipeline stage
├── agents/
│   ├── common/         # Shared Pydantic models + LLM factory
│   ├── parser/         # Requirement parsing (LLM + rule-based)
│   ├── generator/      # Playwright test generation + quality gate
│   ├── execution/      # Playwright subprocess bridge + artifacts
│   ├── discover/       # Coverage discovery from code/docs + live crawl
│   ├── coverage/       # Gap analysis + V8 coverage aggregation
│   ├── regression/     # Screenshot diff (Pillow / Rust) (Phase 2)
│   ├── api_validation/ # API response checks (Phase 2)
│   ├── logs/           # Console/network log analysis (Phase 2)
│   ├── analyzer/       # LLM failure analysis (Phase 3)
│   ├── autofix/        # Selector repair + apply (Phase 4)
│   ├── nl_create/      # NL test creation (Phase 4)
│   └── reporter/       # HTML/PDF reports + GitHub/Slack/Teams/email
├── github/             # GitHub API client, token resolution
├── playwright/         # Config, fixtures, utils, crawl + PDF scripts
├── prompts/            # LLM system prompts (markdown)
├── templates/          # Jinja2 fallback test + HTML report
├── tests/manual/       # Hand-written smoke + visual regression tests
├── tests/generated/    # Generated tests (disposable)
├── docs/               # Guides + tutorials
├── rust/               # zyvor-diff screenshot processor (Phase 4)
├── kubernetes/         # K8s manifests (Phase 3)
└── docker/             # Container image
```

## CI/CD

- **Lint + unit tests**: `.github/workflows/ci.yml` — ruff, pytest (`tests/unit`), and `node --check` on every push/PR
- **Smoke tests**: `.github/workflows/qa-smoke.yml` — push, PR, nightly
- **Multi-browser**: manual `workflow_dispatch` trigger in same workflow
- **Post-deploy**: `.github/workflows/qa-post-deploy.yml` — `repository_dispatch: staging-deployed`
- **Release**: `.github/workflows/release.yml` — on tag push `v*.*.*`, builds and pushes `ghcr.io/hypersdk/zyaiqaagent:v0.4.0` (+ `:latest`) and creates a GitHub Release; see [docs/releases.md](docs/releases.md)

Run the unit suite locally:

```bash
pip install -e ".[dev]"
ruff check .
pytest tests/unit -q
```

## Roadmap Status

| Phase | Status | Features |
|-------|--------|----------|
| **1** | Complete | GitHub integration, Playwright, test gen, CI/CD, HTML + PDF reports |
| **2** | Complete | Screenshot regression, API validation, browser log analysis |
| **3** | Complete | LLM failure analysis, Slack/Teams/email, K8s deployment |
| **4** | Complete | Autofix, NL test creation, multi-browser, Rust processor |

## License

Apache 2.0 — see [LICENSE](LICENSE).
