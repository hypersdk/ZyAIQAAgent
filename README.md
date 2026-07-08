# Zyvor QA Agent

Autonomous AI testing agent for [Zyvor](https://zyvor.dev) — an AI-first infrastructure platform. Continuously validates the Zyvor platform by reading requirements from GitHub, generating Playwright tests, executing them after deployments, detecting regressions, and producing actionable reports.

## Architecture

```
GitHub (specs, PRs, deploy events)
        │
        ▼
LangGraph Orchestrator (Python)
        │
   ┌────┴────┬──────────┬──────────┐
   ▼         ▼          ▼          ▼
 Parser   Generator  Playwright  Analyzer
 (LLM)     (LLM)     (Node.js)   (LLM stub)
   │         │          │          │
   └────┬────┴──────────┴──────────┘
        ▼
   Report Generator → GitHub / Slack / Email
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
# Edit .env with your API keys and repo settings

make install
```

### Run smoke tests (no LLM required)

```bash
zyvor-qa test
```

### Run full pipeline (requires LLM API key)

```bash
zyvor-qa run --source local --spec prompts/examples/vm-create.md
```

### Generate tests only

```bash
zyvor-qa generate --spec prompts/examples/vm-create.md
```

### Start webhook server

```bash
zyvor-qa serve --port 8080
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `zyvor-qa run` | Full pipeline: fetch → parse → generate → execute → report → notify |
| `zyvor-qa test` | Run Playwright smoke tests only |
| `zyvor-qa generate --spec <path>` | Parse spec and generate Playwright tests |
| `zyvor-qa serve` | Start GitHub webhook server |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LLM_PROVIDER` | For AI features | `openai`, `anthropic`, `azure`, `google`, `ollama` |
| `LLM_MODEL` | No | Model name (default: `gpt-4o`) |
| `OPENAI_API_KEY` | If provider=openai | OpenAI API key |
| `ANTHROPIC_API_KEY` | If provider=anthropic | Anthropic API key |
| `GITHUB_TOKEN` | For GitHub source | PAT with `repo` scope |
| `GITHUB_WEBHOOK_SECRET` | For webhook server | HMAC secret for GitHub webhooks |
| `ZYVOR_PRODUCT_REPO` | For GitHub source | e.g. `owner/zyvor-monorepo` |
| `ZYVOR_BASE_URL` | No | Test target (default: `https://zyvor.dev`) |
| `ZYVOR_STAGING_URL` | For dashboard tests | Staging environment URL |
| `ZYVOR_TEST_USER` | For auth tests | Staging login username |
| `ZYVOR_TEST_PASSWORD` | For auth tests | Staging login password |

See [`.env.example`](.env.example) for the full list.

## LLM Provider Setup

Set `LLM_PROVIDER` and the matching API key:

```bash
# OpenAI (default)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Local Ollama
LLM_PROVIDER=ollama
LLM_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

## Project Structure

```
├── orchestrator/       # LangGraph pipeline, CLI, webhook
├── agents/             # Parser, generator, analyzer, reporter, execution
├── playwright/         # Playwright config, fixtures, utils
├── tests/
│   ├── manual/         # Hand-written smoke tests
│   └── generated/      # AI-generated tests
├── prompts/            # LLM system prompts
├── templates/          # Jinja2 templates for tests and reports
├── github/             # GitHub REST client
├── docker/             # Docker image and compose
├── kubernetes/         # K8s manifests (Phase 3)
└── rust/               # Perf-critical processing (Phase 4)
```

## CI/CD

- **Smoke tests**: `.github/workflows/qa-smoke.yml` — runs on push, PR, nightly
- **Post-deploy**: `.github/workflows/qa-post-deploy.yml` — triggered by `repository_dispatch: staging-deployed`

Trigger post-deploy from your product repo:

```bash
gh api repos/owner/ZyAIQAAgent/dispatches \
  -f event_type=staging-deployed
```

## Docker

```bash
make docker
# or
docker compose -f docker/docker-compose.yml up zyvor-qa
```

## Roadmap

| Phase | Status | Features |
|-------|--------|----------|
| **1** | Current | GitHub integration, Playwright, basic test gen, CI/CD, HTML reports |
| **2** | Stub | Screenshot regression, API validation, browser log analysis |
| **3** | Stub | LLM failure analysis, Slack/Teams/email, K8s deployment |
| **4** | Stub | Self-healing selectors, NL test creation, Rust artifact processing |

## License

Apache 2.0 — see [LICENSE](LICENSE).
