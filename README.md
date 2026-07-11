# Zyvor QA Agent

Autonomous AI testing agent for [Zyvor](https://zyvor.dev) — an AI-first infrastructure platform. Continuously validates the Zyvor platform by reading requirements from GitHub, generating Playwright tests, executing them after deployments, detecting regressions, and producing actionable reports.

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

### Prerequisites

- Python 3.9+ (3.11+ recommended)
- Node.js 20+
- Git

### Install

```bash
cp .env.example .env
make install
```

### Run smoke tests (no LLM required)

```bash
zyvor-qa test
```

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

| Guide | Description |
|-------|-------------|
| [**Writing Tests & GitHub Integration**](docs/test-authoring.md) | How tests are created (manual, spec, NL) and how to connect a GitHub repo |
| [`.env.example`](.env.example) | Full environment variable reference |
| [`kubernetes/README.md`](kubernetes/README.md) | Kubernetes deployment |
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
| `zyvor-qa create "description"` | Generate tests from plain English |
| `zyvor-qa create "description" --execute` | Generate and run NL tests |
| `zyvor-qa regression` | Visual regression check |
| `zyvor-qa regression --update-baselines` | Capture new screenshot baselines |
| `zyvor-qa serve` | GitHub webhook server |

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
| NL test creation | `zyvor-qa create` | Generate tests from plain English |
| Multi-browser | `ENABLE_MULTI_BROWSER=true` | Chromium + Firefox + WebKit |
| Rust diff processor | `ENABLE_RUST_PROCESSOR=true` | Fast screenshot diff via `zyvor-diff` binary |

```bash
# Natural language test
zyvor-qa create "Verify homepage shows all 14 products" --execute

# Build Rust diff tool
make rust

# Multi-browser (manual)
ENABLE_MULTI_BROWSER=true npx playwright test
```

## Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

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
├── agents/
│   ├── parser/         # Requirement parsing
│   ├── generator/      # Playwright test generation
│   ├── regression/     # Screenshot diff (Phase 2)
│   ├── api_validation/ # API response checks (Phase 2)
│   ├── logs/           # Console/network log analysis (Phase 2)
│   ├── analyzer/       # LLM failure analysis (Phase 3)
│   ├── autofix/        # Selector repair (Phase 4)
│   ├── nl_create/      # NL test creation (Phase 4)
│   └── reporter/       # Reports + notifications
├── playwright/         # Config, fixtures, utils
├── tests/manual/         # Hand-written smoke + visual regression tests
├── rust/                 # zyvor-diff screenshot processor (Phase 4)
├── kubernetes/           # K8s manifests (Phase 3)
└── docker/               # Container image
```

## CI/CD

- **Smoke tests**: `.github/workflows/qa-smoke.yml` — push, PR, nightly
- **Multi-browser**: manual `workflow_dispatch` trigger in same workflow
- **Post-deploy**: `.github/workflows/qa-post-deploy.yml` — `repository_dispatch: staging-deployed`

## Roadmap Status

| Phase | Status | Features |
|-------|--------|----------|
| **1** | Complete | GitHub integration, Playwright, test gen, CI/CD, HTML + PDF reports |
| **2** | Complete | Screenshot regression, API validation, browser log analysis |
| **3** | Complete | LLM failure analysis, Slack/Teams/email, K8s deployment |
| **4** | Complete | Autofix, NL test creation, multi-browser, Rust processor |

## License

Apache 2.0 — see [LICENSE](LICENSE).
