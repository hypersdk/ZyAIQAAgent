"""Notification delivery — GitHub, Slack, Teams, Email."""

from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText

import httpx

from agents.common.models import PipelineReport


def notify_github_pr(
    repo_full_name: str,
    pr_number: int,
    report: PipelineReport,
) -> bool:
    """Post report summary as a PR comment."""
    from github.client import GitHubClient

    client = GitHubClient()
    body = report.summary
    if report.failure_analysis:
        body += f"\n\n### Failure Analysis\n\n{report.failure_analysis}"
    if report.html_path:
        body += f"\n\nFull report: `{report.html_path}`"

    client.post_pr_comment(repo_full_name, pr_number, body)
    return True


def notify_slack(report: PipelineReport) -> bool:
    """Post to Slack webhook (Phase 3 stub)."""
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False

    payload = {
        "text": (
            f"Zyvor QA: {report.passed}/{report.total} passed. "
            f"{report.failed} failed.\n{report.summary}"
        )
    }
    httpx.post(webhook_url, json=payload, timeout=10)
    return True


def notify_teams(report: PipelineReport) -> bool:
    """Post to Microsoft Teams webhook (Phase 3 stub)."""
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        return False

    payload = {
        "@type": "MessageCard",
        "summary": "Zyvor QA Report",
        "text": report.summary,
    }
    httpx.post(webhook_url, json=payload, timeout=10)
    return True


def notify_email(report: PipelineReport) -> bool:
    """Send email notification (Phase 3 stub)."""
    host = os.environ.get("SMTP_HOST")
    to_addr = os.environ.get("NOTIFY_EMAIL_TO")
    if not host or not to_addr:
        return False

    msg = MIMEText(report.summary)
    msg["Subject"] = f"Zyvor QA Report — {report.passed}/{report.total} passed"
    msg["From"] = os.environ.get("SMTP_USER", "zyvor-qa@localhost")
    msg["To"] = to_addr

    with smtplib.SMTP(host, int(os.environ.get("SMTP_PORT", "587"))) as server:
        user = os.environ.get("SMTP_USER")
        password = os.environ.get("SMTP_PASSWORD")
        if user and password:
            server.starttls()
            server.login(user, password)
        server.send_message(msg)
    return True


def notify_all(
    report: PipelineReport,
    repo_full_name: str | None = None,
    pr_number: int | None = None,
) -> dict[str, bool]:
    """Send notifications to all configured channels."""
    results: dict[str, bool] = {}

    if repo_full_name and pr_number:
        try:
            results["github"] = notify_github_pr(repo_full_name, pr_number, report)
        except Exception:
            results["github"] = False

    results["slack"] = notify_slack(report)
    results["teams"] = notify_teams(report)
    results["email"] = notify_email(report)

    return results
