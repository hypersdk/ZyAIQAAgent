# Roadmap

Known gaps and deliberate deferrals, consolidated in one place instead of
scattered across runbooks, docstrings, and CI config comments. This is
inventory, not a promise sheet — no dates, just what's open and where the
detail already lives.

## Test coverage — in progress

Overall unit-test coverage moved from ~33% to ~39% by targeting the two
worst-covered files:

- `orchestrator/dashboard/jobs.py` — 19% → 33%. `_validate()` (all ~25 job
  kinds, not just a handful) plus the state/dispatch layer (`log_progress`,
  `_stream_line*`, `cancel`/`status`, `trigger`/`_run`, `_brief`, `_slug`,
  `_explain_failure`, `_cases_payload`, `_env_overrides`,
  `_safe_local_spec` — including a real path-traversal-rejection test) are
  now covered (`tests/unit/test_jobs_validate.py`,
  `tests/unit/test_jobs_state.py`).
- `orchestrator/cli.py` — 0% → 19%. `_initial_state`, `_load_env`,
  `_ensure_tls_cert` covered (`tests/unit/test_cli_helpers.py`).

**Deliberately still uncovered** in both files: the ~30 `_job_*` /
`@app.command()` functions themselves. They're thin wrappers that
immediately delegate to real subprocess/network calls (Playwright, crawl
scripts, TLS probes, HTTP probes) — meaningfully unit-testing them means
mocking `subprocess.run`/network I/O per job kind for a large effort-to-value
ratio, versus the validation/state layer above where bugs actually bite
(input validation, path safety, dispatch correctness) and where coverage is
now real. That's still the next slice if coverage needs to go further.

The CI gate (`.github/workflows/security.yml`) currently enforces
`--cov-fail-under=28` — quietly relaxed down from an original 70% target
that was never actually met, with an inline `TODO` rather than a plan to
close the gap. Worth raising the gate to reflect the ~39% floor now that
it's real, and continuing to close the gap from there.

## Observability: tracing

`orchestrator/observability/metrics.py` provides Prometheus-style
counters/gauges (`/api/v2/metrics`, scope-gated) but there's no distributed
tracing (OpenTelemetry or otherwise) and only two modules use structured
logging (`logging.getLogger`) — most of the pipeline reports progress via an
ad-hoc redacted buffer (`orchestrator/dashboard/jobs.py`'s `log_progress`).
Fine for a single-process pipeline; would matter more once the job queue
scales past one instance (see below).

## Horizontal scale: Postgres-backed store

`MissionControlStore` (`orchestrator/persistence/store.py`) is SQLite —
single-writer, matching the current single-replica K8s deployment
(`kubernetes/deployment.yaml`). This is a deliberate, self-documented
choice, not an oversight — the store's own docstring says the repository
interface is "deliberately small so a PostgreSQL implementation can replace
it without changing API routes." Worth doing once there's an actual need to
run more than one Mission Control instance.

## Scheduler: single-flight, drops missed ticks

Already documented operationally in
[`docs/devops/04-mission-control-ops.md`](docs/devops/04-mission-control-ops.md#3-scheduled-checks-optional):
schedules are single-flight (a tick is skipped, not queued, if the previous
run is still in flight), and the runbook is explicit that schedules are for
human alerting, not a substitute for the CI gate. Cross-linked here so it
doesn't get "discovered" again as a surprise.

## ~~CSRF~~ — done

Was flagged, then reconsidered as low-value (`SameSite=Lax` + `HttpOnly`
already covers most of it), then built anyway: double-submit-cookie CSRF
protection (`orchestrator/dashboard/auth.py`'s `csrf_token_for`/`csrf_valid`,
enforced in `orchestrator/webhook.py`'s `auth_middleware` for mutating
`/api/*` requests authenticated via the session cookie). The frontend side
is a single `window.fetch` wrapper in `templates/dashboard.html.j2` that
attaches `X-CSRF-Token` automatically — none of the ~20 existing `fetch()`
call sites needed touching individually. Covered by
`tests/unit/test_csrf_route.py` (real login → protected-route round trip)
and `tests/unit/test_auth.py`.
