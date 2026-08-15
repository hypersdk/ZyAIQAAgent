# Changelog

## [Unreleased]

### Added
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
