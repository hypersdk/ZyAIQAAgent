# Changelog

## Unreleased

### Added
- Dedicated unit tests for `orchestrator/security/rbac.py` (`tests/unit/test_security_rbac.py`) — the token/session identification and scope-enforcement layer gating every `/api/v2` route had zero direct tests, only incidental coverage (58%) from routes that happen to call through it. Now 100%: Bearer-token lookup (role→scope mapping, unknown-role fallback to `viewer`, explicit extra-scope grants, no-match → 401), session-cookie identification (authenticated → `admin`, not authenticated → 401), the local-development fallback and its production fail-closed counterpart, and `require_scope`'s 403 path.
- Dedicated unit tests for `orchestrator/security/secrets.py` (`tests/unit/test_security_secrets.py`) — the secret-reference guard/resolver used for durable schedules, queued jobs, and the `host_pentest`/`cloud_pentest` credential path had zero direct tests, only incidental coverage (67%). Now 100%: `assert_persistable`'s raw-value rejection under a secret-shaped key (recursing correctly through nested dicts/lists, and correctly *not* iterating strings/bytes as sequences), `_validate_ref`'s `env:`/`file:` format checks, and `resolve_secret`'s three failure modes (missing env var, missing file, oversized file).
- Closed out the remaining gaps in `orchestrator/security/` so the whole package is now 100% covered:
  - `agent_policy.py` (76% → 100%, `tests/unit/test_agent_policy.py`) — the browser-action safety policy's control-char stripping, `from_env` parsing, element/index validation, cross-origin navigation gating, and every `classify_action` risk branch (read/input/privileged/write/destructive).
  - `target_policy.py` (82% → 100%, `tests/unit/test_target_policy.py`) — the SSRF-resistant URL/host validator's full input-validation ladder (empty/overlong/bad-scheme/missing-hostname/blocked-metadata-host/invalid-port/unresolvable-host), CIDR-based allowlisting, and the `validate_target_url`/`validate_target_host` module-level wrappers.
  - `sandbox.py` (77% → 100%, `tests/unit/test_sandbox.py`) — the egress-`NetworkPolicy` apply/cleanup paths (success and failure), the job-status polling loop's multi-iteration case, pod-log-read failure handling, and every "cleanup failure must not propagate" branch in `run_python`'s `finally` block.
  - `config.py`, `webhook.py`, `redaction.py`, `rate_limit.py`, `slack.py` — the last few untested branches in each (unrestricted-agent-mode and disabled-engagement-enforcement production checks, GitHub webhook signature/delivery-id rejection paths, `redact`'s max-depth/tuple/set branches, the rate limiter's inline stale-entry trim racing its own periodic prune sweep, Slack's missing/malformed-timestamp rejection).
- Together these passes move the CI gate's own coverage metric (`--cov=orchestrator --cov=agents`) from 43.65% to 45.15%, 510 tests total. `orchestrator/security/` (11 modules) is now fully covered.

## [0.7.0](https://github.com/hypersdk/zyvor-argus/releases/tag/v0.7.0) — 2026-08-16

### Changed
- Renamed the project from ZyAIQAAgent / Zyvor QA Agent to **Zyvor Argus** — the tool had grown well past "QA agent" into autonomous testing, security probing, red-teaming, monitoring, and chat-ops. `Zyvor` stays the umbrella brand (company, `zyvor.dev` target platform, `ZYVOR_*` env vars); only the tool's own identity changes.
  - CLI binary is now `argus`, restructured from 26 flat commands into grouped subcommands: `argus test` (run/exec/generate/discover/create/import-codegen), `argus flow` (run/realtime), `argus vision` (regression/route-sweep), `argus api` (test/ai-test/auth-test/har-replay), `argus watch` (vitals/audit), `argus guard` (misconfig-scan/cve-lookup/exploit-poc/attack-chain/host-pentest/cloud-pentest/pr-gate), `argus redteam llm`, `argus ask` (ingest/evaluate), and `argus serve` (unchanged, top-level). The old flat `zyvor-qa <verb>` form is kept as a deprecated alias for a transition period.
  - Package renamed `zyvor-qa-agent` → `zyvor-argus`; MCP server identifier and console script `zyvor-qa-mcp` → `argus`/`argus-mcp` (no alias); desktop app → `Zyvor Argus`/`zyvor-argus-desktop`; Docker image `ghcr.io/hypersdk/zyaiqaagent` → `ghcr.io/hypersdk/zyvor-argus`.
  - Docker/Kubernetes/CI manifests, deploy tooling, GitHub Action, CI/CD templates, and ~250 files of documentation updated to match. GitHub repo renamed `hypersdk/ZyAIQAAgent` → `hypersdk/zyvor-argus` (old URL redirects).

## [0.6.0](https://github.com/hypersdk/zyvor-argus/releases/tag/v0.6.0) — 2026-08-16

### Added
- CI now catches classes of regression it previously didn't: `.github/workflows/ci.yml` gained a `docs-and-manifests` job that validates every Kubernetes manifest offline (`scripts/validate_k8s_manifests.py`), fails if `docs/customer/` has drifted from `routes.json`/`page-purposes.json` (`npm run docs:guides` must produce no diff), and checks every customer-doc relative link (`npm run docs:links`) — found and fixed a real broken-link regression from this exact gap before adding the check. New `.github/workflows/codeql.yml` (GitHub CodeQL, Python + JS/TS, on push/PR/weekly) and `.github/dependabot.yml` (weekly PRs for pip, npm root + `desktop/`, cargo `desktop/src-tauri/`, Docker, and GitHub Actions — each runs through the full existing CI before merge)
- MCP server (`integrations/mcp/`, optional `argus-mcp` / `[mcp]` extra) exposing an allowlisted subset of `/api/v2` jobs as MCP tools (`run_job`, `run_smoke_test`, `run_site_audit`, `run_crawl_test`, `get_job_status`, `cancel_job`) so any MCP-capable chat agent (e.g. Hermes Agent) can trigger and poll QA jobs from Telegram/Discord/Slack/CLI. Thin HTTP client of the existing `/api/v2` API — no `orchestrator.*` imports — reuses the existing Bearer-token RBAC scopes with no security-layer changes. Bounded server-side polling (default 20s, cap 90s) resolves fast jobs (smoke/ping/probes) in a single chat turn; slower jobs hand back a job id to poll later. See `docs/mcp-server.md`
- `ZYVOR_API_TOKENS_FILE` is now actually mountable in Kubernetes: `kubernetes/deployment.yaml` and `kubernetes/enterprise/secure-deployment.yaml` mount a `argus-secrets` key (`api-tokens.json`) at `/app/secrets/api-tokens.json` — previously the env var was documented and read by `orchestrator/security/rbac.py` but never wired into any manifest, so Bearer-token auth was a dead end in the production (`ZYVOR_ENV=production`) deployment
- Security-testing capabilities, scoped to what's safe to bolt onto an existing trusted-job runner (see `ROADMAP.md` for what's deliberately deferred and why):
  - A general-purpose security-engagement authorization primitive (`orchestrator/security/engagement_policy.py`, `engagements` table in `orchestrator/persistence/store.py`, `POST/GET/DELETE /api/v2/engagements`) — an admin-issued, target-scoped, tier-ranked attestation that gates every elevated-risk job kind below, enforced at `_validate()` so no caller (dashboard, CLI, `/api/v2/jobs`, schedules) can bypass it. Mirrors `orchestrator/security/agent_policy.py`'s mode/fail-closed-in-production shape
  - `misconfig_scan` job/CLI command: tech + version fingerprinting, wordlist-driven path discovery (`agents/probes/data/misconfig_paths.txt`, ~150 paths vs. the existing `security_paths` probe's static 7), security-header *value* grading (not just presence), SPF/DMARC/CAA DNS hygiene checks
  - `cve_lookup` job/CLI command: read-only — fingerprints tech/versions, checks them against OSV.dev. No PoC is generated or run
  - `llm_redteam` job/CLI command: attacker→judge loop (curated ~15-prompt battery, `agents/redteam/`) against argus's own "Ask Zyvor" RAG agent, covering prompt injection, system-prompt exfiltration, excessive agency, jailbreaks, and PII/secret exfiltration — the first job kind able to raise a `critical`-severity finding
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

### Fixed
- `container-scan` CI job: `agents/redteam/prompts/llm_redteam_battery.yaml`'s `pii-02` adversarial prompt used a synthetic token that structurally matched GitHub's real PAT format exactly (`ghp_` + 36 chars), which Trivy's secret scanner correctly flagged as CRITICAL once baked into the built image — even though it was never a real credential. Replaced with a placeholder that no longer matches the pattern; the red-team test's intent is unaffected

## [0.5.1](https://github.com/hypersdk/zyvor-argus/releases/tag/v0.5.1) — 2026-08-15

### Fixed
- Desktop app: when `argus` can't be found/spawned, the error now surfaces immediately instead of after a 30-second retry budget — found by actually downloading and running the v0.5.0 release build without a `argus` install present, not just testing the happy path. The loading screen's poll loop was retrying on every failure regardless of whether it was recoverable; the Rust side only ever rejects for a genuine, permanent failure (a transient "still starting" state returns successfully with no result), so there was nothing to gain by waiting

## [0.5.0](https://github.com/hypersdk/zyvor-argus/releases/tag/v0.5.0) — 2026-08-15

### Added
- Native macOS desktop app (`desktop/`, Tauri 2): a thin shell around `argus serve` — spawns it bound to `127.0.0.1`, points a native window at its dashboard, kills it on quit. No reimplementation; every dashboard action goes through the same server, job queue, CSRF, and rate limiting as `argus serve` normally. Settings UI (⌘,) to override the resolved binary path. See Tutorial 17 and `desktop/README.md`
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

## [0.4.0](https://github.com/hypersdk/zyvor-argus/releases/tag/v0.4.0) — 2026-08-06

### Added
- Reusable Docker-based GitHub Action (`action.yml`) so any repo can run `argus` as a QA gate via `uses: hypersdk/zyvor-argus@v0.7.0`
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
- `ghcr.io/hypersdk/zyvor-argus:v0.4.0` (+ `:latest`)

## [0.3.0](https://github.com/hypersdk/zyvor-argus/releases/tag/v0.3.0) — 2026-07-30

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
- `ghcr.io/hypersdk/zyvor-argus:v0.3.0` (+ `:latest`)

## [0.2.0](https://github.com/hypersdk/zyvor-argus/releases/tag/v0.2.0) — 2026-07-29

Initial GHCR-published feature release with Mission Control journeys, HAR/codegen, and zyvor.dev demo assets.
