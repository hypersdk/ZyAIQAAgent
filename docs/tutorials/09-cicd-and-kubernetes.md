# Tutorial 9 — CI/CD & Kubernetes

Run the agent automatically: GitHub Actions for smoke and post-deploy pipelines, Docker for packaging, Kubernetes for the always-on webhook and nightly runs.

**Prerequisites:** Tutorials [1](01-getting-started.md) and [4](04-github-integration.md).

---

## 1. GitHub Actions (included workflows)

Two workflows ship in `.github/workflows/`:

### `qa-smoke.yml` — fast feedback

Triggers: push to `main`, PRs to `main`, nightly at 06:00 UTC, manual dispatch.

- **`smoke` job**: installs Python + Node + Chromium, runs `argus test exec` against `https://zyvor.dev`, uploads `reports/` + `test-results/` as artifacts (14-day retention).
- **`multi-browser` job**: manual `workflow_dispatch` only — runs `tests/manual/` on chromium + firefox + webkit.

### `qa-post-deploy.yml` — full pipeline after deploys

Trigger: `repository_dispatch` with type `staging-deployed`. Runs `argus test run --source github` with LLM analysis, regression, and Slack notification.

Fire it from your product repo's deploy job:

```yaml
- name: Trigger QA
  run: |
    gh api repos/<owner>/<qa-agent-repo>/dispatches \
      -f event_type=staging-deployed
  env:
    GH_TOKEN: ${{ secrets.QA_DISPATCH_TOKEN }}
```

### Repository configuration

Set under **Settings → Secrets and variables → Actions**:

| Kind | Name | Purpose |
|------|------|---------|
| Variable | `ZYVOR_PRODUCT_REPO` | `owner/repo` of the product |
| Variable | `ZYVOR_BASE_URL` | deployment under test (default `https://zyvor.dev`) |
| Variable | `LLM_PROVIDER` / `LLM_MODEL` | provider selection (defaults `openai` / `gpt-4o`) |
| Secret | `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | whichever matches the provider |
| Secret | `SLACK_WEBHOOK_URL` | optional notifications |

## 2. Docker

Build and run the container (multi-stage: Node + Playwright Chromium layered onto Python):

```bash
make docker
# or manually:
docker build -f docker/Dockerfile -t zyvor-argus .
docker run --env-file .env zyvor-argus                 # default: run --source local
docker run --env-file .env zyvor-argus test            # any CLI subcommand
docker run --env-file .env -p 8080:8080 zyvor-argus serve --port 8080 --host 0.0.0.0
```

The entrypoint is `argus`, so container args are CLI args.

## 3. Kubernetes

Manifests in `kubernetes/` deploy two workloads from the same image:

| Manifest | Workload |
|----------|----------|
| `deployment.yaml` + `service.yaml` + `ingress.yaml` | Webhook server (`argus serve`) with `/health` liveness/readiness probes |
| `cronjob.yaml` | Nightly smoke tests (`argus test exec`, 06:00 UTC) |
| `configmap.yaml` | Feature flags and URLs |
| `secret.yaml` | API keys and tokens (use ExternalSecrets or SOPS in production) |

Deploy:

```bash
# 1. Build/push the image somewhere your cluster can pull, then update image: in the manifests
# 2. Put real values in configmap.yaml / secret.yaml
# 3. Validate offline (no cluster needed):
make k8s-validate

# 4. Apply (requires a reachable cluster — make checks first):
make k8s-apply

# Server-side dry-run against the cluster:
make k8s-validate-cluster

# Tear down:
make k8s-delete
```

Local cluster for testing: `kind create cluster --name argus` or `minikube start`, then `kubectl cluster-info` to confirm.

Point the GitHub webhook at the ingress host you set in `kubernetes/ingress.yaml` (default manifest placeholder is `qa-webhook.example.com`):

```
https://qa-webhook.example.com/webhook/github
```

with the same `GITHUB_WEBHOOK_SECRET` as in `secret.yaml`.

## 4. Choosing a deployment pattern

| Need | Use |
|------|-----|
| PR checks + nightly smoke, no infra | GitHub Actions only |
| Instant webhook-triggered runs, LLM features, persistent reports | K8s webhook Deployment |
| Scheduled deep runs (regression + coverage + autofix) | K8s CronJob with those flags, or Actions `schedule` |
| One-off local runs | CLI / Docker |

They compose — most setups run Actions smoke on PRs *and* the webhook server for post-deploy validation.

## 5. CI tips

- `argus test run` and `argus test exec` exit non-zero on failure — safe as gating steps.
- Always upload `reports/`, `test-results/`, `screenshots/`, `videos/`, `traces/` with `if: always()` so failures keep their evidence.
- Commit `screenshots/baselines/` if you enable regression in CI; otherwise every CI run starts baseline-less.
- Keep `ENABLE_AUTOFIX_APPLY=false` in CI unless the workflow commits the patch as a reviewable PR.

---

That's the full tour. Reference docs: [Architecture](../architecture.md) · [Configuration](../configuration.md) · [Troubleshooting](../troubleshooting.md) · [Command reference](../test-authoring.md).
