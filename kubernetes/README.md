# Kubernetes Deployment (Phase 3)

Run Zyvor QA Agent on Kubernetes.

## Manifests

| File | Purpose |
|------|---------|
| `configmap.yaml` | Non-secret configuration (feature flags, URLs) |
| `secret.yaml` | API keys, tokens (use ExternalSecrets in production) |
| `cronjob.yaml` | Nightly smoke tests (`zyvor-qa test`) |
| `deployment.yaml` | Webhook server (`zyvor-qa serve`) |
| `service.yaml` | ClusterIP service for webhook |
| `ingress.yaml` | External access to GitHub webhook endpoint |

## Deploy

```bash
# Edit secret.yaml with your API keys first
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/cronjob.yaml
kubectl apply -f kubernetes/ingress.yaml
```

Or use the Makefile:

```bash
make k8s-apply
```

## GitHub Webhook

Point your GitHub webhook to:
```
https://qa-webhook.zyvor.dev/webhook/github
```

Events: `push`, `pull_request`, `repository_dispatch`
