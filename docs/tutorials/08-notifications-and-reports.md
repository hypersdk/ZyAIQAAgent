# Tutorial 8 — Notifications & Reports

Get results where your team lives: HTML/PDF reports, GitHub PR comments, Slack, Microsoft Teams, and email.

**Prerequisites:** [Tutorial 1](01-getting-started.md).

---

## 1. Report anatomy

Every pipeline run ends with `report → notify`. The HTML report (`reports/qa-summary.html`) contains:

- summary line (LLM plain-English when `ENABLE_LLM_REPORT=true`, stats block otherwise)
- per-test table: status, browser, duration, error messages
- links to failure artifacts — screenshot, video, trace (copied under `reports/artifacts/<test>/`)
- sections for visual regression diffs, API validation failures, log issues, autofix suggestions, and V8 coverage when those features are on

The **PDF** (`reports/qa-summary.pdf`) is the same report printed via headless Chromium — useful for email and audit trails. Controlled by `ENABLE_PDF_REPORT` (default `true`); regenerate manually with `npm run report:pdf`.

There is also Playwright's own interactive report: `npm run report`.

## 2. GitHub PR comments

Covered in [Tutorial 4](04-github-integration.md#5-post-results-to-a-pull-request) — automatic whenever both a repo and PR number are known (`--pr-number` flag or webhook PR event). The comment includes status emoji, summary, coverage stats, failure analysis, and suggested fixes.

## 3. Slack

Create an [incoming webhook](https://api.slack.com/messaging/webhooks) for your channel, then:

```bash
# .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T…/B…/…
```

Every run posts a block-formatted message: header with PASSED/FAILED, pass/fail/total fields, the summary, and (on failure) the first 500 characters of failure analysis.

Test it without waiting for a real run:

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"argus webhook test"}' "$SLACK_WEBHOOK_URL"
```

This is outbound only. For the opposite direction — triggering a run *from* Slack — see [Tutorial 16](16-slack-gateway.md).

## 4. Microsoft Teams

Create an incoming webhook connector on the target channel, then:

```bash
# .env
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/…
```

Runs post a MessageCard — green theme on pass, red on fail, with the same stats and summary.

## 5. Email (with PDF attached)

```bash
# .env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=qa-bot@example.com
SMTP_PASSWORD=…
NOTIFY_EMAIL_TO=team@example.com
```

Sends a multipart email (plain + HTML) with subject like `Zyvor Argus Report — FAILED (10/12)`. When the PDF report exists, it's attached. STARTTLS + login are used when credentials are set; a local unauthenticated relay works by leaving user/password empty.

## 6. Channel behavior

- Channels are **independent and optional** — each activates only when its variables are set; you can enable any combination.
- Delivery failures are isolated: one channel erroring never blocks the others or fails the pipeline. `notify_all()` returns per-channel success booleans (visible in webhook server logs).
- All channels fire on **every** run, pass or fail. If you only want failure noise, wrap the CLI in CI logic (e.g. run `notify` channels only on non-zero exit) — see [Tutorial 9](09-cicd-and-kubernetes.md).

**Next:** [Tutorial 9 — CI/CD & Kubernetes](09-cicd-and-kubernetes.md).
