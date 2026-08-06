# Releases & Container Image

Tagged releases are published automatically by [`.github/workflows/release.yml`](../.github/workflows/release.yml).

**Current release:** [v0.4.0](https://github.com/hypersdk/ZyAIQAAgent/releases/tag/v0.4.0)

## What happens on a release

Pushing a tag matching `v*.*.*` (e.g. `v0.4.0`) to the `hypersdk/ZyAIQAAgent` repo:

1. Builds the container image from [`docker/Dockerfile`](../docker/Dockerfile).
2. Pushes it to GHCR as `ghcr.io/hypersdk/zyaiqaagent:<tag>` and `:latest`.
3. Creates a GitHub Release on the tag with auto-generated notes.

## Pulling the image

```bash
docker pull ghcr.io/hypersdk/zyaiqaagent:v0.4.0
# or track latest
docker pull ghcr.io/hypersdk/zyaiqaagent:latest

docker run --rm --env-file .env ghcr.io/hypersdk/zyaiqaagent:v0.4.0 test
```

The image entrypoint is `zyvor-qa` (see [`docker/Dockerfile`](../docker/Dockerfile)); pass any `zyvor-qa` subcommand as the container command, e.g. `serve --port 8080 --host 0.0.0.0`.

No k3s/Kubernetes cluster is required to run it — it's a normal container. A single Pod works fine against any existing cluster too:

```bash
kubectl run zyvor-qa --image=ghcr.io/hypersdk/zyaiqaagent:v0.4.0 \
  --env="ZYVOR_BASE_URL=https://zyvor.dev" \
  -- serve --port 8080 --host 0.0.0.0
```

The [`kubernetes/`](../kubernetes/README.md) manifests and the k3s path in [`docs/remote-deploy.md`](remote-deploy.md) are only for when you want a managed Deployment/Service, not a requirement.

GHCR packages inherit repo visibility by default — if the repo is private, `docker pull` requires `docker login ghcr.io` with a token that has `read:packages`.

## Cutting a release

```bash
# bump pyproject.toml / package.json first, then:
git tag v0.3.1
git push hypersdk v0.3.1
# or, to also create the GitHub Release explicitly:
gh release create v0.3.1 --repo hypersdk/ZyAIQAAgent --generate-notes
```

Either the tag push or the `gh release create` triggers the workflow (it also accepts `workflow_dispatch` with an existing tag, for re-publishing an image without cutting a new release). Version numbers follow `pyproject.toml` / `package.json` (currently `0.3.0`); bump those alongside the tag. See [CHANGELOG.md](../CHANGELOG.md).
