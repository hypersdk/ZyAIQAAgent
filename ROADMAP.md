# Roadmap

Known gaps and deliberate deferrals, consolidated in one place instead of
scattered across runbooks, docstrings, and CI config comments. This is
inventory, not a promise sheet — no dates, just what's open and where the
detail already lives.

## Test coverage — in progress

Overall unit-test coverage moved from ~33% to ~42% (389 tests) across two
passes: the validation/state-layer pass below, then the security-testing
feature pass (`engagement_policy.py` 100%, `sandbox.py` 77%, `jobs.py`'s new
`exploit_poc`/`attack_chain`/`host_pentest`/`cloud_pentest`/`misconfig_scan`/
`cve_lookup`/`llm_redteam` validation and state paths) adding its own tests
on top without moving the needle down.

- `orchestrator/dashboard/jobs.py` — 19% → 46%. `_validate()` (all job
  kinds, not just a handful) plus the state/dispatch layer (`log_progress`,
  `_stream_line*`, `cancel`/`status`, `trigger`/`_run`, `_brief`, `_slug`,
  `_explain_failure`, `_cases_payload`, `_env_overrides`,
  `_safe_local_spec` — including a real path-traversal-rejection test) are
  now covered (`tests/unit/test_jobs_validate.py`,
  `tests/unit/test_jobs_state.py`, plus the new security-job test files).
- `orchestrator/cli.py` — 0% → 17%. `_initial_state`, `_load_env`,
  `_ensure_tls_cert` covered (`tests/unit/test_cli_helpers.py`).

**Deliberately still uncovered** in both files: most of the `_job_*` /
`@app.command()` functions themselves. They're thin wrappers that
immediately delegate to real subprocess/network calls (Playwright, crawl
scripts, TLS probes, HTTP probes) — meaningfully unit-testing them means
mocking `subprocess.run`/network I/O per job kind for a large effort-to-value
ratio, versus the validation/state layer above where bugs actually bite
(input validation, path safety, dispatch correctness) and where coverage is
now real. That's still the next slice if coverage needs to go further.

The CI gate (`.github/workflows/security.yml`) enforces
`--cov-fail-under=40` (raised from 36, itself raised from an original,
never-actually-met 70% target) — still a deliberate few points below the
measured ~42% floor to leave headroom for minor cross-Python-version
coverage variance, with an inline `TODO` to keep raising it as coverage
grows rather than a plan to close the whole gap at once.

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

## Desktop app v2: single-binary freeze

`desktop/` (Tauri 2 shell) ships a native macOS window around
`zyvor-qa serve`, but v1 deliberately wraps an *existing* local install
(the repo's own `.venv`, or `zyvor-qa` on `PATH`) rather than bundling a
self-contained runtime — see `desktop/README.md` and the plan that shipped
it. Two real blockers stand between that and a true single-binary/`.pkg`
distribution someone could install without a dev checkout:

- **`_repo_root()` isn't frozen-binary-aware.** `Path(__file__).resolve().
  parents[N]`, used throughout `webhook.py`, `routes.py`, `jobs.py`,
  `cli.py`, `nodes/*.py` to locate `templates/`, `prompts/`, `tests/`,
  `reports/`, assumes a real filesystem checkout. A PyInstaller freeze (the
  approach `hypercluster/cli/hypercluster.spec` uses for its own Python CLI)
  would silently fail to find its own templates unless every one of those
  call sites is taught to check `sys.frozen`/`sys._MEIPASS` first — a
  repo-wide audit, not a packaging afterthought.
- **Playwright's browser binaries aren't freezable.** They're downloaded
  separately via `npx playwright install` (hundreds of MB per browser), so
  even a fully frozen Python side would still need Node + Playwright
  bundled alongside it — closer in size/complexity to the existing
  `docker/Dockerfile` multi-stage build than to a lightweight desktop
  installer.

Code signing + notarization config is wired up (`make desktop-build-signed`,
`desktop/README.md`'s "Code signing & notarization" section) but not
actually usable without an Apple Developer account's credentials, which
this session doesn't have — so it's configured, not done. Still fully
open: a Windows/NSIS build (hypercluster's `desktop-pkg-windows` target is
the template if this becomes worth doing).

## ~~Active exploitation~~ — done (PoC generation/execution, attack chaining, host/cloud pentesting)

Built in four stages during a security-testing feature pass rather than all
at once. Foundation: a general-purpose security-engagement authorization
primitive (`orchestrator/security/engagement_policy.py`,
`orchestrator/persistence/store.py`'s `engagements` table,
`POST/GET/DELETE /api/v2/engagements`) that gates elevated-risk job kinds
behind an admin-issued, target-scoped, tier-ranked attestation — mirroring
`orchestrator/security/agent_policy.py`'s mode/approved-risks/fail-closed-
in-production shape. Seven job kinds sit behind it: `misconfig_scan`,
`cve_lookup`, `llm_redteam` at the `active_recon` tier, and `exploit_poc`,
`attack_chain`, `host_pentest`, `cloud_pentest` at the `exploit` tier.

### ~~PoC generation/execution~~ — done, verification-only

`exploit_poc` (`orchestrator/dashboard/jobs.py`, `agents/exploit/
poc_generator.py`, `orchestrator/security/sandbox.py`) generates a
non-destructive verification script via LLM for a described finding, then
runs it — never in the job-runner process — as a short-lived Kubernetes Job
in a dedicated namespace (`kubernetes/sandbox.yaml`): dropped capabilities,
non-root, read-only rootfs, no ServiceAccount token, resource limits, a hard
wall-clock timeout. Gated by two independent things, not one: the citing
engagement must be `tier=exploit` (`active_recon` is rejected), *and*
`ZYVOR_EXPLOIT_EXECUTION_ENABLED=true` must be set — mirroring
`AgentPolicy`'s `allow_destructive` pattern, so an admin creating an
`exploit`-tier engagement alone can't turn this on by accident. If no
sandbox namespace is configured or the cluster is unreachable,
`sandbox.available()` returns false and the job refuses to run rather than
falling back to unsandboxed execution. The generated script's system prompt
constrains it to read-only requests, no floods/DoS, and a single
`VERIFIED: true/false - reason` output line grounded in a timing/response/
status-code difference — not a destructive payload. PoC source is written to
`reports/pocs/<run>/poc.py` with its SHA-256 logged to `audit_events`.

Network-egress restriction is attempted (a per-Job NetworkPolicy scoped to
the target's resolved IPs) but is explicitly best-effort: it only has real
effect on NetworkPolicy-enforcing CNIs (Calico, Cilium, EKS/GKE/AKS default
addons) — k3s's default Flannel CNI does not enforce NetworkPolicy at all,
so on a plain k3s cluster this specific layer is a no-op and the pod
security hardening above is what's actually holding. See
`kubernetes/sandbox.yaml`'s comments for the full caveat.

**Live-verified** against a real k3s cluster (not just the mocked-client
unit tests in `tests/unit/test_sandbox.py`/`test_exploit_poc_job.py`):
`sandbox.run_python()` genuinely creates a Job, runs code under the
hardened `securityContext`, retrieves its output, and tears everything down
— confirmed zero leftover Jobs/Pods/ConfigMaps across repeated runs. This
live pass also caught and fixed a real bug: the Kubernetes client
occasionally returns a pod's log as the `str()` of a `bytes` object rather
than a decoded string (the exact quirk `orchestrator/dashboard/k8s.py`
already works around for the dashboard's own log viewer —
`_normalize_log_text`, now reused by `sandbox.py` too). The LLM-generation
side (`poc_generator.py`) is unit-tested with a mocked model only; it
wasn't live-exercised against a real LLM provider in this pass.

### ~~Attack chaining~~ — done

`attack_chain` (`orchestrator/dashboard/jobs.py::_job_attack_chain`,
`agents/exploit/poc_generator.py::plan_next_chain_step`) repeatedly
plan-and-verifies one escalation step at a time — an LLM planner proposes
the next step given every step already confirmed, `poc_generator.py`
generates its verification script exactly as `exploit_poc` does, and it
runs through the identical sandboxed executor. The chain stops the moment a
step fails to verify or the planner has nothing safe left to propose
(capped at 5 steps either way) — it does not blindly retry or brute-force
past a failed step. Same two-gate authorization as `exploit_poc`
(`exploit`-tier engagement + `ZYVOR_EXPLOIT_EXECUTION_ENABLED`). A confirmed
multi-step chain raises an additional `critical`-severity finding
summarizing the full escalation path, on top of one `high`-severity finding
per individual confirmed step.

The sequential-execution mechanic (multiple `sandbox.run_python()` calls in
a row, each with its own Job/ConfigMap lifecycle) was live-verified against
the same k3s cluster — three consecutive runs, zero leftover resources, no
naming collisions. The LLM planning loop itself
(`plan_next_chain_step`/`generate_verification_poc` deciding what to
verify next) is unit-tested with a mocked model only, same caveat as above.

### ~~Credentialed host/cloud pentesting~~ — done (host SSH; cloud AD/WinRM not included)

`host_pentest` (SSH, via `paramiko`) and `cloud_pentest` (`aws`/`gcloud`/`az`
CLIs) close out the full NeuroSploit-inspired scope. Credentials are never
accepted as raw job params — `orchestrator/security/secrets.py`'s
`{"$secret": "env:..."}` reference pattern is required (enforced via
`assert_persistable()` in `_validate()`), resolved only at execution time,
and injected directly into the one ephemeral sandbox Job's environment —
never logged, never embedded in LLM-generated code, never present in the
job result (verified by dedicated unit tests, `tests/unit/
test_pentest_jobs.py`, that plant a real-looking secret value and assert it
never appears in the returned result or any audit-log call).

The default sandbox image (`python:3.12-slim`) has neither `paramiko` nor
the cloud CLIs, so `sandbox.py` gained an `image` override
(`ZYVOR_SANDBOX_HOST_IMAGE`/`ZYVOR_SANDBOX_CLOUD_IMAGE`) — both job kinds
fail closed with a clear error if the relevant image env var isn't set,
same "refuse rather than silently downgrade" posture as everywhere else in
this feature set. A **third**, independent opt-in —
`ZYVOR_CREDENTIALED_PENTEST_ENABLED=true` — gates these on top of
`exploit_poc`'s existing two gates (exploit-tier engagement +
`ZYVOR_EXPLOIT_EXECUTION_ENABLED`), since using real credentials against
real infrastructure is a materially bigger step than generating/running a
verification script against a URL.

**Live-verified** the custom-image mechanic against the real k3s cluster:
built a minimal `python:3.12-slim` + `paramiko` image, imported it into the
cluster, and ran it as a real sandboxed Job — which caught and fixed a real
bug (Kubernetes defaults `:latest`-tagged images to `imagePullPolicy:
Always`, so it tried to pull the locally-built image from a registry
instead of using what was already on the node; `sandbox.py` now sets
`IfNotPresent` explicitly). Did **not** live-test an actual SSH connection
end-to-end — that would have required adding a new key to the test host's
`authorized_keys`, a standing access-control change judged out of scope for
a one-off verification pass. `cloud_pentest` is code-complete and
unit-tested only; no cloud credentials were available in this pass to
verify it live.

Not included: Active Directory-specific tooling (Kerberos/LDAP enumeration,
WinRM) beyond generic SSH, and any lateral-movement/persistence logic — the
scope here is read-only enumeration and non-destructive verification, same
as every other job kind in this feature set.

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
