# ZyAIQAAgent Enterprise v2

Integration guide for the enterprise security and durable control-plane overlay.

## What the installer changes

The installer copies the overlay into the existing repository and patches three current files:

1. `orchestrator/webhook.py`
   - installs the `/api/v2` enterprise router and durable workers
   - requires webhook signatures unless explicitly allowed for development
   - requires `X-GitHub-Delivery`
   - rejects replayed delivery IDs
2. `orchestrator/dashboard/jobs.py`
   - uses recursive secret redaction
   - validates every URL and hostname through the target policy before execution
3. `agents/aiflow/engine.py`
   - passes every LLM/heuristic action through the deterministic safety gateway

It replaces the old in-memory `scheduler.py` and `findings.py` with compatible SQLite-backed implementations. Backups are written beside changed files with a `.v1-backup` suffix.

## New API

### Queue a durable job

```bash
curl -X POST https://qa.example.com/api/v2/jobs \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: deployment-7f0a1' \
  -d '{
    "kind": "vitals",
    "params": {"url": "https://app.example.com", "device": "Desktop Chrome"}
  }'
```

### Queue a job with a secret reference

```json
{
  "kind": "realtime",
  "params": {
    "url": "https://app.example.com",
    "ws": "/ws/events",
    "token": {"$secret": "env:QA_REALTIME_TOKEN"}
  }
}
```

Raw tokens and passwords are rejected for persisted jobs and schedules.

### Service tokens

Create a random token, hash it with SHA-256, and store only its hash:

```bash
python tools/hash_api_token.py
```

Set `ZYVOR_API_TOKENS_FILE=/run/secrets/zyvor/api-tokens.json`.

Example file:

```json
{
  "<sha256>": {
    "subject": "github-actions",
    "role": "operator"
  }
}
```

Roles:

- `viewer`: read jobs, findings, schedules, audit and engagements
- `operator`: run/cancel jobs, manage schedules/findings, read engagements
- `admin`: all scopes, including creating/revoking engagements (`engagements:write`)

Only `admin` can create or revoke a security engagement — see
[Security engagements](#security-engagements) below.

## Target policy

```bash
export ZYVOR_TARGET_ALLOWLIST='zyvor.dev,*.zyvor.dev,customer.example.com'
export ZYVOR_TARGET_ALLOWED_PORTS='80,443,24631'
export ZYVOR_TARGET_ALLOWED_CIDRS='10.20.0.0/16'
export ZYVOR_ALLOW_PRIVATE_TARGETS=false
export ZYVOR_ALLOW_HTTP_TARGETS=false
```

Even when a hostname is allowlisted, metadata IPs remain blocked. Every resolved address and redirect destination must pass policy.

The live-crawl agent (`playwright/scripts/crawl-site.mjs`) has its own, narrower guard (`playwright/scripts/lib/target-policy.mjs`) for the same purpose — it validates every page navigated to during the BFS, not just the initial URL, since the crawler follows arbitrary in-site links. It blocks the same private/loopback/link-local/metadata ranges by default; set `CRAWL_ALLOW_PRIVATE_TARGETS=true` only for local dev targets.

## Security engagements

Three job kinds do deeper, potentially-invasive security testing —
`misconfig_scan` (misconfig/recon beyond the static probes), `cve_lookup`
(read-only, checks fingerprinted versions against OSV.dev), and
`llm_redteam` (adversarial-prompt battery against Ask Zyvor) — and are
refused (`400`) unless the request cites a live, sufficiently-scoped
**security engagement**: an `admin`-issued attestation that the target is
actually authorized for testing. This is separate from (and in addition to)
the SSRF-focused [target policy](#target-policy) above — target policy
blocks *unsafe* destinations (private ranges, cloud metadata); engagements
answer *is this specific test run actually authorized*.

Create one (requires `engagements:write`, i.e. `admin`):

```bash
curl -X POST https://qa.example.com/api/v2/engagements \
  -H 'Content-Type: application/json' \
  -d '{
    "target_pattern": "*.example.com",
    "scope_statement": "authorized pentest, staging + prod, 2026-Q3 engagement",
    "tier": "active_recon",
    "expires_at": "2026-10-01T00:00:00+00:00"
  }'
```

Then pass its `id` as `engagement_id` in the job's params:

```bash
curl -X POST https://qa.example.com/api/v2/jobs \
  -H 'Content-Type: application/json' \
  -d '{"kind": "misconfig_scan", "params": {"url": "https://app.example.com", "engagement_id": "<id>"}}'
```

`target_pattern` matches the job's hostname via the same `fnmatch` glob style
as `ZYVOR_TARGET_ALLOWLIST` (e.g. `*.example.com`, or `*` for "any host" in a
trusted dev environment). `tier` is `active_recon` today for all three job
kinds — `exploit` is reserved for the not-yet-built PoC-execution phase (see
`ROADMAP.md`). Revoke with `DELETE /api/v2/engagements/{id}`; list with
`GET /api/v2/engagements` (`engagements:read`, available to `viewer` too).

`ZYVOR_ENGAGEMENT_ENFORCEMENT=disabled` turns this gate off entirely (e.g.
for local dev) — refused at startup when `ZYVOR_ENV=production`, same
fail-closed pattern as the unrestricted-agent-mode check below.

## Autonomous-agent modes

- `read_only`: assertions, waits, navigation and non-submitting UI exploration
- `supervised`: write actions require an approved risk class
- `unrestricted`: writes allowed, but destructive actions remain disabled by default

```bash
export ZYVOR_AGENT_MODE=supervised
export ZYVOR_AGENT_APPROVED_RISKS=write
export ZYVOR_AGENT_ALLOW_DESTRUCTIVE=false
export ZYVOR_AGENT_ALLOWED_ORIGINS='login.example.com,sso.example.com'
```

The agent blocks unknown actions, invalid indices, disabled controls, unapproved cross-origin navigation, suspicious page instructions and destructive actions.

## Persistence

Default database:

```text
reports/mission-control.db
```

Override:

```bash
export ZYVOR_STATE_DB=/var/lib/zyvor-qa/mission-control.db
```

SQLite is appropriate for one control-plane replica. Use PostgreSQL and an external queue before scaling control-plane replicas horizontally.

## Secure Kubernetes deployment

```bash
kubectl apply -f kubernetes/enterprise/secure-deployment.yaml
kubectl apply -f kubernetes/enterprise/network-policy.yaml
```

Pod restart is deliberately excluded from default RBAC. Apply `optional-pod-restart-rbac.yaml` only when required.
