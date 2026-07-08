# Kubernetes Deployment (Phase 3)

Run Zyvor QA Agent as a scheduled CronJob or webhook Deployment.

## Planned manifests

- `cronjob.yaml` — nightly smoke tests
- `deployment.yaml` — webhook server for post-deploy triggers
- `configmap.yaml` — non-secret configuration
- `secret.yaml` — API keys (use external secrets operator in production)

## Status

Stub only — add manifests when deploying to Zyvor-managed K8s clusters.
