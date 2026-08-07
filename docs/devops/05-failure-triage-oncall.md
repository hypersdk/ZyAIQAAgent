# 05 — Failure triage (on-call)

**Goal:** CI/Mission Control went red. Decide in ≤15 minutes: infra vs product bug vs flake vs policy.

---

## 1. Grab evidence first (don’t re-run blind)

From the failed GitHub Actions run (or GitLab artifacts):

| Artifact | Why |
|----------|-----|
| `reports/summary.json` | command, counts, status, duration |
| `reports/qa-summary.html` / job HTML | human narrative |
| `test-results/**/trace.zip` | Playwright trace (open with `npx playwright show-trace`) |
| `videos/`, `*.webm` | flow failures |
| `screenshots/diffs/` | visual / route-sweep |
| Job log around “target rejected” / net::ERR | policy / network |

```bash
jq '{status,passed,failed,command,target_url,duration_s,extra}' reports/summary.json
```

---

## 2. Decision tree

```text
summary.json missing?
  └─ Action/container crashed early → check image pull, entrypoint, OOM
status=failed, failed>0
  └─ open HTML / trace → assertion vs timeout vs 5xx from app
log: target rejected by policy
  └─ runbook 02 — allowlist / ZYVOR_ENV
log: net::ERR_CONNECTION / DNS
  └─ runner cannot reach staging — network, not product
log: Timeout waiting for selector
  └─ feature not deployed, flag off, or selector drift → product/QA
intermittent, same test ~30% fail
  └─ flake — quarantine + ticket; raise workers/shards carefully
LLM command failed immediately
  └─ missing key / provider outage — smoke should not need LLM
```

---

## 3. Classify & route

| Class | Page | Example |
|-------|------|---------|
| **P1 infra** | DevOps / platform | Staging down, DNS, cert, runner outage |
| **P1 product** | Owning squad | Checkout broken after deploy |
| **P2 contract** | API squad | OpenAPI drift / undeclared 500 |
| **P3 flake** | QA | Timing; add wait / stabilize |
| **P3 policy** | DevOps | Allowlist typo after hostname change |

Comment on the PR/deploy with: **class**, **summary.json snippet**, **artifact link**, **next action**.

---

## 4. Safe re-run protocol

1. Confirm staging still on the failing revision (`/health` or build id header).  
2. Re-run **failed job only** once.  
3. If green on re-run with no change → open flake ticket; do not “just ignore” forever.  
4. If still red → do not keep clicking Re-run; fix code or quarantine.

Report-only mode (`fail-on-error: false`) is for **rollout**, not for permanent mute of a hard gate.

---

## 5. Quarantine pattern

```ts
test.skip(true, 'INC-1234: flaky billing CTA — until 2026-08-20');
// or grep-exclude in CI temporarily:
// grep: '@smoke' with test tagged @quarantine removed from smoke
```

Track quarantine in the same sprint board as the bug. Expired quarantine = P2.

---

## 6. Mission Control live failure

- Open **Findings** / **QA Runs** / live job panel.  
- **Stop** stuck jobs (don’t stack schedules).  
- Download CSV/HTML/PDF from the job.  
- If dashboard itself is down: `curl /health`, systemd/container status, disk full (Playwright leftovers).

```bash
# remote examples
systemctl status zyvor-qa   # name may vary per deploy
df -h
docker ps | grep zyvor
```

---

## 7. Post-incident (short blameless)

Capture in the ticket:

- Deploy ID / git SHA under test  
- Gate command + grep/shard  
- Root cause class  
- Fix PR  
- Whether pin/image changed  

Update runbooks if policy or runner labels were wrong.
