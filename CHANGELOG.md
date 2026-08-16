# Changelog

## Unreleased

### Added
- MCP server (`integrations/mcp/`, optional `zyvor-qa-mcp` / `[mcp]` extra) exposing an allowlisted subset of `/api/v2` jobs as MCP tools (`run_job`, `run_smoke_test`, `run_site_audit`, `run_crawl_test`, `get_job_status`, `cancel_job`) so any MCP-capable chat agent (e.g. Hermes Agent) can trigger and poll QA jobs from Telegram/Discord/Slack/CLI. Thin HTTP client of the existing `/api/v2` API — no `orchestrator.*` imports — reuses the existing Bearer-token RBAC scopes with no security-layer changes. Bounded server-side polling (default 20s, cap 90s) resolves fast jobs (smoke/ping/probes) in a single chat turn; slower jobs hand back a job id to poll later. See `docs/mcp-server.md`
- `ZYVOR_API_TOKENS_FILE` is now actually mountable in Kubernetes: `kubernetes/deployment.yaml` and `kubernetes/enterprise/secure-deployment.yaml` mount a `zyvor-qa-secrets` key (`api-tokens.json`) at `/app/secrets/api-tokens.json` — previously the env var was documented and read by `orchestrator/security/rbac.py` but never wired into any manifest, so Bearer-token auth was a dead end in the production (`ZYVOR_ENV=production`) deployment
- Security-testing capabilities, scoped to what's safe to bolt onto an existing trusted-job runner (see `ROADMAP.md` for what's deliberately deferred and why):
  - A general-purpose security-engagement authorization primitive (`orchestrator/security/engagement_policy.py`, `engagements` table in `orchestrator/persistence/store.py`, `POST/GET/DELETE /api/v2/engagements`) — an admin-issued, target-scoped, tier-ranked attestation that gates every elevated-risk job kind below, enforced at `_validate()` so no caller (dashboard, CLI, `/api/v2/jobs`, schedules) can bypass it. Mirrors `orchestrator/security/agent_policy.py`'s mode/fail-closed-in-production shape
  - `misconfig_scan` job/CLI command: tech + version fingerprinting, wordlist-driven path discovery (`agents/probes/data/misconfig_paths.txt`, ~150 paths vs. the existing `security_paths` probe's static 7), security-header *value* grading (not just presence), SPF/DMARC/CAA DNS hygiene checks
  - `cve_lookup` job/CLI command: read-only — fingerprints tech/versions, checks them against OSV.dev. No PoC is generated or run
  - `llm_redteam` job/CLI command: attacker→judge loop (curated ~15-prompt battery, `agents/redteam/`) against zyvor-qa's own "Ask Zyvor" RAG agent, covering prompt injection, system-prompt exfiltration, excessive agency, jailbreaks, and PII/secret exfiltration — the first job kind able to raise a `critical`-severity finding
  - CI/CD security gate: `--fail-on <severity>` on `audit`/`misconfig-scan`/`cve-lookup`/`llm-redteam` (new `audit` CLI command — it previously had none), plus `pr-gate` posting a REQUEST_CHANGES/APPROVE PR review + commit status (`github_integration/client.py` gains `create_pr_review`/`set_commit_status`/`get_pr_head_sha`, using PyGithub methods that were already a transitive dependency)
  - Attack-graph reporting: findings now carry a `category` field (OWASP/informal tags), rendered as a same-origin Mermaid graph (`agents/reporter/attack_graph.py`, vendored `templates/vendor/mermaid.min.js` — the CSP's `script-src 'self'` blocks a CDN `<script>`) embedded in the audit report
  - `exploit_poc` job/CLI command: generates a non-destructive verification script via LLM for a described finding and runs it in a short-lived, locked-down Kubernetes Job (`orchestrator/security/sandbox.py`, `kubernetes/sandbox.yaml`) — dropped capabilities, non-root, read-only rootfs, no ServiceAccount token, resource limits, hard timeout — never in the job-runner process. Gated by two independent things: an `exploit`-tier engagement *and* a separate `ZYVOR_EXPLOIT_EXECUTION_ENABLED=true` opt-in. Refuses to run (does not fall back to unsandboxed execution) if no cluster/namespace is configured. Live-verified against a real k3s cluster — found and fixed a real pod-log decoding bug in the process
  - `attack_chain` job/CLI command: repeatedly plan-and-verify one escalation step at a time (LLM planner → PoC generator → sandboxed execution, reusing `exploit_poc`'s exact machinery), stopping the moment a step fails to verify or the planner has nothing safe left to propose (capped at 5 steps). Same two-gate authorization as `exploit_poc`. A confirmed multi-step chain raises an additional `critical` finding summarizing the full escalation path
  - `host_pentest`/`cloud_pentest` job/CLI commands: generate a non-destructive SSH (`paramiko`) or cloud-CLI (`aws`/`gcloud`/`az`) enumeration script via LLM and run it in a specially-imaged sandbox Job (`ZYVOR_SANDBOX_HOST_IMAGE`/`ZYVOR_SANDBOX_CLOUD_IMAGE` — the default `python:3.12-slim` image lacks this tooling, so these fail closed rather than silently running without it). Credentials are supplied as `{"$secret": "env:NAME"}` references (`orchestrator/security/secrets.py`), resolved only at execution time and injected straight into the one ephemeral Job's environment — never logged, never embedded in generated code, never present in the job result. A *third*, independent opt-in — `ZYVOR_CREDENTIALED_PENTEST_ENABLED=true` — gates these on top of `exploit_poc`'s existing two gates, since using real credentials against real infrastructure is a bigger step than generating/running a verification script against a URL. `sandbox.py` also gained an `image` override and explicit `imagePullPolicy: IfNotPresent` (found live: Kubernetes defaults `:latest`-tagged images to `Always`, which fails to pull a locally-built/imported custom image that was never pushed to a registry). This closes out the full NeuroSploit-inspired "active exploitation" scope from `ROADMAP.md`
- Mission Control UI for the four new security job kinds above (`exploit_poc`, `attack_chain`, `host_pentest`, `cloud_pentest`) — dashboard cards, command-palette entries, and result-panel rendering
- Tutorial 18 (`docs/tutorials/18-security-testing.md`) covering the full security-testing feature set end to end: engagements, recon/red-team jobs, the CI gate, and the sandboxed exploitation tiers with their opt-in gates
- Markdown report export (`agents/reporter/exports.py`): every per-job report bundle (smoke/flow/checks/realtime/vitals/api-contract/route-sweep/audit) now also writes `report.md` — a GitHub-flavored table with pass/fail badges and a failure-details section, generated locally with no external tool (always available even with `ENABLE_PDF_REPORT=false`). Dashboard gets a **⬇ Markdown** download button plus a one-click **⧉ Copy MD** that puts the report straight on the clipboard, mirroring the existing Ask Zyvor "copy as Markdown" pattern; `GET /api/dashboard/jobs/report.md` added alongside the existing `.csv`/`.html`/`.pdf` route

### Changed
- CI's unit-test coverage gate raised from 36% to 40% (`.github/workflows/security.yml`) after the security-testing feature pass added its own coverage (~39% → ~42% actual, 389 tests)
- `kubernetes/ingress.yaml`'s webhook hostname is no longer hardcoded to `qa-webhook.zyvor.dev` — it's now a `qa-webhook.example.com` placeholder with a `# CHANGE ME` comment, so the manifest doesn't silently point at Zyvor's own domain when someone deploys it to their own cluster

## [0.5.1](https://github.com/hypersdk/ZyAIQAAgent/releases/tag/v0.5.1) — 2026-08-15

### Fixed
- Desktop app: when `zyvor-qa` can't be found/spawned, the error now surfaces immediately instead of after a 30-second retry budget — found by actually downloading and running the v0.5.0 release build without a `zyvor-qa` install present, not just testing the happy path. The loading screen's poll loop was retrying on every failure regardless of whether it was recoverable; the Rust side only ever rejects for a genuine, permanent failure (a transient "still starting" state returns successfully with no result), so there was nothing to gain by waiting

## [0.5.0](https://github.com/hypersdk/ZyAIQAAgent/releases/tag/v0.5.0) — 2026-08-15

### Added
- Native macOS desktop app (`desktop/`, Tauri 2): a thin shell around `zyvor-qa serve` — spawns it bound to `127.0.0.1`, points a native window at its dashboard, kills it on quit. No reimplementation; every dashboard action goes through the same server, job queue, CSRF, and rate limiting as `zyvor-qa serve` normally. Settings UI (⌘,) to override the resolved binary path. See Tutorial 17 and `desktop/README.md`
- Persistent "skill" memory for the autofix loop (`agents/skills/`): a selector fix that's patched and confirmed passing is remembered and reused directly next run instead of re-derived by the LLM every time
- Inbound Slack slash-command gateway (`POST /webhook/slack/command`): `/zyvor run <kind>` / `/zyvor status <job_id>` trigger and check on pipeline runs from chat, HMAC-verified via `SLACK_SIGNING_SECRET` (Tutorial 16)
- Per-IP rate limiting on `/api/dashboard/*` and `/api/v2/*` (`orchestrator/security/rate_limit.py`), 429 + `Retry-After` once `ZYVOR_API_RATE_LIMIT` is exceeded — previously only the login endpoint had any throttling
- Double-submit-cookie CSRF protection for the Mission Control dashboard: mutating `/api/*` requests authenticated via the session cookie now require a matching `X-CSRF-Token` header (`orchestrator/dashboard/auth.py`, enforced in `orchestrator/webhook.py`); the dashboard's own JS attaches it automatically via a single `fetch` wrapper, no template call sites needed touching
- `ROADMAP.md` consolidating known gaps (test coverage, tracing, horizontal scale) that were otherwise scattered across runbooks and CI comments

### Changed
- `regression`/`api_validate`/`log_analyze`/`v8_coverage` now run in parallel off of `execute` instead of a forced sequential chain, joining at a new `merge_results` node — reduces pipeline wall-clock on every run and retry
- Failure-analysis LLM context is now bounded: capped failed-case count, truncated per-case logs/error text, filtered to failing regression/API/log entries only (previously every entry, passing included, went into the prompt unfiltered)
- `MissionControlStore.recover_stale_jobs()` now dead-letters (marks `failed`) a job once its attempt count hits `ZYVOR_JOB_MAX_ATTEMPTS`, instead of requeuing a crash-looping job forever
- CI's unit-test coverage gate raised from 28% to 36% (`.github/workflows/security.yml`) after covering `orchestrator/dashboard/jobs.py`'s validation/state layer and `orchestrator/cli.py`'s helpers (~33% → ~39% actual coverage)

### Fixed
- The failure-analysis prompt no longer globs every historical failure video out of the repo-wide `videos/` directory — only the current run's artifacts are included

## [0.4.0](https://github.com/hypersdk/ZyAIQAAgent/releases/tag/v0.4.0) — 2026-08-06

### Added
- Reusable Docker-based GitHub Action (`action.yml`) so any repo can run `zyvor-qa` as a QA gate via `uses: hypersdk/ZyAIQAAgent@v0.4.0`
- Copy-paste CI templates for GitLab CI, CircleCI, Jenkins, and Azure Pipelines (`templates/ci/`)
- Stable `reports/summary.json` CI contract, written by `run`/`test`/`flow`/`route-sweep`/`vitals`
- Tutorial 15: external CI/CD integration guide

### Fixed
- `route-sweep` and `vitals` previously always exited 0, even on regressions — both now exit 1 on failure
- The repo's own `github/` package shadowed the installed `PyGithub` library, silently breaking GitHub-source pipelines on editable installs — renamed to `github_integration/`
- TLS certificate verification was unconditionally disabled across all 10 HTTP probes + ping/loadtest (a logic bug made an `insecure` toggle a no-op)
- 11 HTML report templates rendered with Jinja2 autoescaping off (XSS risk on untrusted page content in generated reports)
- `knowledge/security.py` no longer trusts a client-supplied `X-Tenant-ID` header by default when no `AUTH_TOKENS_JSON` mapping is configured (`TRUST_CLIENT_TENANT_HEADER` opt-in for trusted deployments)
- Live-crawl agent now validates every crawled URL (not just the initial target) against an SSRF/private-range guard, closing a redirect/DNS-rebinding gap
- CI: pinned ruff's rule `select` explicitly after a ruff version bump silently widened its own default rules and broke lint; fixed 45 real mypy errors; scoped bandit's ~99 findings down to the real ones (now fixed) plus a documented skip list; patched known CVEs in transitive deps and the container image's bundled npm/setuptools

### Container
- `ghcr.io/hypersdk/zyaiqaagent:v0.4.0` (+ `:latest`)

## [0.3.0](https://github.com/hypersdk/ZyAIQAAgent/releases/tag/v0.3.0) — 2026-07-30

### Added
- **Ask Zyvor** — optional citation-first knowledge RAG (`knowledge/` package, Qdrant hybrid retrieval) in Mission Control; Tutorial 14
- Streaming ask (`POST /v1/qa/stream`, dashboard SSE), query understanding, evidence-based confidence
- Optional read-only live cluster diagnostic tools (namespaced allowlist)
- Separate HITL remediation planner + allowlisted pod-restart executor
- Mission Control → GuestKit YouTube demo: https://youtu.be/ys7SvKKqf9w
- Sample knowledge corpus, ingest/evaluate CLIs, unit tests for knowledge

### Docs
- YouTube thumbnail embeds in README, Tutorial 10/13, customer manuals
- Configuration + `.env.knowledge.example` for knowledge / remediation flags
- Feature guide: Ask Zyvor + demo links

### Container
- `ghcr.io/hypersdk/zyaiqaagent:v0.3.0` (+ `:latest`)

## [0.2.0](https://github.com/hypersdk/ZyAIQAAgent/releases/tag/v0.2.0) — 2026-07-29

Initial GHCR-published feature release with Mission Control journeys, HAR/codegen, and zyvor.dev demo assets.
