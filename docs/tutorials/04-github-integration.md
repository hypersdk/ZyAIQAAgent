# Tutorial 4 — GitHub Integration

Connect a product repository as the requirement source: fetch specs and issues, run the pipeline against them, post results as PR comments, and stand up the webhook server for automatic runs.

**Prerequisites:** [Tutorial 1](01-getting-started.md); a GitHub repo you can read (your product repo).

---

## 1. Authenticate

Two options, in resolution order:

```bash
# Option A (recommended): GitHub CLI
gh auth login

# Option B: token in .env
GITHUB_TOKEN=ghp_...
```

The token needs `Contents: Read`; add `Pull requests: Write` if you want PR comments. Verify:

```bash
gh auth token   # should print a token
```

## 2. Point at your product repo

In `.env`:

```bash
ZYVOR_PRODUCT_REPO=ssahani/hypersdk-web    # owner/repo — not a URL
ZYVOR_BASE_URL=https://zyvor.dev           # where the product is deployed
```

Sanity check:

```bash
curl -s -H "Authorization: Bearer $(gh auth token)" \
  https://api.github.com/repos/$ZYVOR_PRODUCT_REPO | grep full_name
```

## 3. Run from a single spec file in the repo

```bash
# Repo-relative path
argus test run --source github --spec docs/specs/my-feature.md

# Blob and raw URLs also work
argus test run --source github \
  --spec https://github.com/ssahani/hypersdk-web/blob/main/docs/specs/my-feature.md
```

The file is downloaded to `tests/fixtures/fetched/`, then the normal parse → generate → execute → report pipeline runs.

## 4. Run from everything (no --spec)

```bash
argus test run --source github
```

Without `--spec`, the agent fetches **all default sources**:

| Source | Saved as |
|--------|----------|
| Open issues labeled `qa`, `user-story`, `feature-spec`, or `enhancement` | `tests/fixtures/fetched/issue-<n>.md` |
| Every `.md` in `docs/specs/` | `spec-<i>.md` |
| `CHANGELOG.md`, `README.md` | `spec-<i>.md` |

**Workflow tip:** make `qa`-labeled issues your test backlog. Write acceptance criteria in the issue body, label it, and the next run picks it up.

## 5. Post results to a pull request

```bash
argus test run --source github --spec docs/specs/my-feature.md --pr-number 42
```

After the run, the agent comments on PR #42 with pass/fail counts, the LLM summary (when enabled), failure analysis, coverage stats, and suggested fixes. The PR body itself is also fetched and parsed as an additional spec source, and the PR's changed files scope coverage discovery (see [Tutorial 5](05-coverage-expansion.md)).

## 6. Automatic runs: the webhook server

For push/PR/deploy-triggered runs without CI wiring:

```bash
# In .env — reject unsigned payloads:
GITHUB_WEBHOOK_SECRET=<random-string>

argus serve --port 8080
```

On your product repo: **Settings → Webhooks → Add webhook**

- Payload URL: `https://<your-host>:8080/webhook/github`
- Content type: `application/json`
- Secret: the same `GITHUB_WEBHOOK_SECRET`
- Events: `push`, `pull_request`, plus `repository_dispatch` if your deploy pipeline emits `staging-deployed`

Behavior per event:

| Event | What runs |
|-------|-----------|
| `pull_request` | Full pipeline; results commented on the PR |
| `push` | Full pipeline; changed files scope coverage discovery |
| `repository_dispatch` (`staging-deployed`) | Full post-deploy pipeline |

Local testing without a public host:

```bash
argus serve --port 8080 &
curl -s http://localhost:8080/health          # {"status":"ok"}
# then use a tunnel (e.g. `ssh -R`, ngrok, cloudflared) for real GitHub delivery
```

To trigger the post-deploy flow from your deployment pipeline:

```bash
gh api repos/$ZYVOR_PRODUCT_REPO/dispatches \
  -f event_type=staging-deployed \
  -F 'client_payload[pr_number]=42'
```

## 7. Generate-only from GitHub

To review generated tests before ever running them:

```bash
argus test generate --source github --spec docs/specs/my-feature.md
git diff tests/generated/
```

**Next:** [Tutorial 5 — Coverage expansion](05-coverage-expansion.md): let the agent read your repo's code and docs to find what your tests miss.
