# Tutorial 16 — Slack slash-command gateway

Trigger and check on pipeline runs from chat: `/zyvor run smoke` starts a job, `/zyvor status <job_id>` checks on it — without opening Mission Control.

**Prerequisites:** [Tutorial 1](01-getting-started.md), [Tutorial 10](10-mission-control-dashboard.md) (the gateway enqueues onto the same job queue Mission Control uses).

---

## 1. How it's different from Tutorial 8's Slack notifications

[Tutorial 8](08-notifications-and-reports.md#3-slack) covers `SLACK_WEBHOOK_URL` — **outbound only**: every run posts its result to a fixed channel. This tutorial covers the opposite direction: an inbound Slack **slash command** that can *start* a run. The two are independent and commonly used together — trigger with `/zyvor run smoke`, get the result posted back via the Tutorial 8 webhook once it finishes.

## 2. Create the Slack app

1. [Create a Slack app](https://api.slack.com/apps) (from scratch, in your workspace).
2. Under **Slash Commands**, create a command named `/zyvor` with the request URL set to your Mission Control server: `https://<your-host>/webhook/slack/command`.
3. Under **Basic Information → App Credentials**, copy the **Signing Secret**.
4. Install the app to your workspace.

## 3. Configure the agent

```bash
# .env
SLACK_SIGNING_SECRET=<the signing secret from step 2.3>
```

That's the only required variable — there's no bot token or OAuth scope to configure, since the gateway only replies synchronously to the command itself (see §5).

## 4. Use it

```
/zyvor run smoke
/zyvor run full
/zyvor run regression
/zyvor run audit
/zyvor status <job_id>
```

`run` accepts one of `smoke`, `full`, `regression`, `audit` — the same job kinds Mission Control's dashboard can trigger. It replies immediately with the enqueued job's id; `status` looks that id up and reports its current state (`queued`, `running`, `succeeded`, `failed`).

## 5. Test it without a real Slack app

Requests are HMAC-verified (`orchestrator/security/slack.py`) — Slack signs every request with `v0:{timestamp}:{body}` over `SLACK_SIGNING_SECRET`, sent as `X-Slack-Signature` / `X-Slack-Request-Timestamp`. You can replicate that locally:

```bash
SECRET="dev-signing-secret"
BODY="command=%2Fzyvor&text=run+smoke&user_name=local-test"
TS=$(date +%s)
SIG="v0=$(printf 'v0:%s:%s' "$TS" "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $NF}')"

curl -X POST "http://localhost:8080/webhook/slack/command" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Slack-Signature: $SIG" \
  -H "X-Slack-Request-Timestamp: $TS" \
  --data "$BODY"
```

Run `zyvor-qa serve` in another terminal first (see [Tutorial 10](10-mission-control-dashboard.md)), with `SLACK_SIGNING_SECRET=dev-signing-secret` set to match.

## 6. Security notes

- Requests are rejected outright if `SLACK_SIGNING_SECRET` isn't set — there's no unsigned fallback (unlike the GitHub webhook's `ZYVOR_ALLOW_UNSIGNED_WEBHOOKS` escape hatch, which doesn't apply here).
- Signatures older than 5 minutes are rejected as stale, defending against replay of a captured request.
- The route is exempt from Mission Control's dashboard session auth (`orchestrator/dashboard/auth.py`) — the Slack signature *is* the authentication for this endpoint, the same way `/webhook/github`'s HMAC signature is.
- It replies synchronously, inside Slack's 3-second window, and does not poll the job to post a follow-up when it finishes — pair it with Tutorial 8's `SLACK_WEBHOOK_URL` if you want completion posted automatically, or run `/zyvor status <job_id>` again later.

**See also:** [docs/architecture.md](../architecture.md) for how the gateway fits into the pipeline's entry points, and the [DevOps runbooks](../devops/README.md) for operating Mission Control's job queue in production.
