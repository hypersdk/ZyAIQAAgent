# Roadmap

Known gaps and deliberate deferrals, consolidated in one place instead of
scattered across runbooks, docstrings, and CI config comments. This is
inventory, not a promise sheet — no dates, just what's open and where the
detail already lives.

## Test coverage

Overall unit-test coverage is ~33%, concentrated unevenly. The CI gate
(`.github/workflows/security.yml`) currently enforces `--cov-fail-under=28`
— quietly relaxed down from an original 70% target that was never actually
met, with an inline `TODO` rather than a plan to close the gap. The two
highest-leverage targets:

- `orchestrator/dashboard/jobs.py` — 1416 lines, 19% covered. Core job
  orchestration logic; `tests/unit/test_jobs_validate.py` already covers
  `_validate()` and is the natural file to extend next.
- `orchestrator/cli.py` — 410 lines, 0% covered. The `zyvor-qa` entry point
  itself has no test coverage at all.

Raising the gate back toward something real is a multi-session initiative
in its own right, not something to bolt onto a hygiene pass.

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

## CSRF: already substantially mitigated, not a build item

An earlier audit pass flagged "no CSRF protection" from a `grep -r csrf`
turning up nothing. On closer inspection: the session cookie
(`orchestrator/dashboard/routes.py`) is already `httponly=True,
samesite="lax", secure=<when https>`, and every state-changing dashboard
call in `templates/dashboard.html.j2` uses explicit POST/DELETE — no
GET-triggers-a-mutation routes. `SameSite=Lax` already blocks cross-site
fetch/XHR and cross-site POST-navigation from attaching the cookie, which is
the standard modern mitigation for this class of app. Building a
double-submit-cookie token system on top would be redundant risk across the
template's ~20 live `fetch()` call sites for little real gain — noted here
so it isn't "fixed" again later without re-deriving this reasoning.
