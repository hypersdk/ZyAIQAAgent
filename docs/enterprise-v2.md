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

- `viewer`: read jobs, findings, schedules and audit
- `operator`: run/cancel jobs and manage schedules/findings
- `admin`: all scopes

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
