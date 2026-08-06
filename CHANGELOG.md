# Changelog

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
