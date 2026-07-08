"""Notification delivery — GitHub, Slack, Teams, Email."""

from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional

import httpx

from agents.common.models import PipelineReport


def _status_emoji(report: PipelineReport) -> str:
    return "✅" if report.failed == 0 else "❌"


def notify_github_pr(
    repo_full_name: str,
    pr_number: int,
    report: PipelineReport,
) -> bool:
    """Post report summary as a PR comment."""
    from github.client import GitHubClient

    client = GitHubClient()
    body = f"{_status_emoji(report)} {report.summary}"
    if report.failure_analysis:
        body += f"\n\n### Failure Analysis\n\n{report.failure_analysis}"
    if report.autofix_suggestions:
        body += "\n\n### Suggested Fixes\n"
        for suggestion in report.autofix_suggestions:
            body += f"- `{suggestion}`\n"
    if report.html_path:
        body += f"\n\n📄 Full report: `{report.html_path}`"

    client.post_pr_comment(repo_full_name, pr_number, body)
    return True


def notify_slack(report: PipelineReport) -> bool:
    """Post rich Slack notification with blocks."""
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False

    status = "PASSED" if report.failed == 0 else "FAILED"
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"Zyvor QA Report — {status}"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Passed:*\n{report.passed}"},
                    {"type": "mrkdwn", "text": f"*Failed:*\n{report.failed}"},
                    {"type": "mrkdwn", "text": f"*Total:*\n{report.total}"},
                ],
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": report.summary}},
        ]
    }

    if report.failure_analysis:
        payload["blocks"].append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Failure Analysis:*\n{report.failure_analysis[:500]}",
                },
            }
        )

    response = httpx.post(webhook_url, json=payload, timeout=15)
    return response.status_code == 200


def notify_teams(report: PipelineReport) -> bool:
    """Post Microsoft Teams adaptive card."""
    webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        return False

    status = "PASSED" if report.failed == 0 else "FAILED"
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": f"Zyvor QA Report — {status}",
        "themeColor": "2EB886" if report.failed == 0 else "D13438",
        "title": f"Zyvor QA Report — {status}",
        "sections": [
            {
                "facts": [
                    {"name": "Passed", "value": str(report.passed)},
                    {"name": "Failed", "value": str(report.failed)},
                    {"name": "Total", "value": str(report.total)},
                ],
                "text": report.summary,
            }
        ],
    }

    response = httpx.post(webhook_url, json=payload, timeout=15)
    return response.status_code == 200


def notify_email(report: PipelineReport) -> bool:
    """Send HTML email notification."""
    host = os.environ.get("SMTP_HOST")
    to_addr = os.environ.get("NOTIFY_EMAIL_TO")
    if not host or not to_addr:
        return False

    status = "PASSED" if report.failed == 0 else "FAILED"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Zyvor QA Report — {status} ({report.passed}/{report.total})"
    msg["From"] = os.environ.get("SMTP_USER", "zyvor-qa@localhost")
    msg["To"] = to_addr

    text_body = report.summary
    if report.failure_analysis:
        text_body += f"\n\nFailure Analysis:\n{report.failure_analysis}"

    html_body = f"""
    <html><body>
    <h2>Zyvor QA Report — {status}</h2>
    <p>Passed: {report.passed} | Failed: {report.failed} | Total: {report.total}</p>
    <pre>{report.summary}</pre>
    {"<h3>Failure Analysis</h3><pre>" + report.failure_analysis + "</pre>" if report.failure_analysis else ""}
    </body></html>
    """

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

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
    repo_full_name: Optional[str] = None,
    pr_number: Optional[int] = None,
) -> Dict[str, bool]:
    """Send notifications to all configured channels."""
    results: Dict[str, bool] = {}

    if repo_full_name and pr_number:
        try:
            results["github"] = notify_github_pr(repo_full_name, pr_number, report)
        except Exception:
            results["github"] = False

    for channel, fn in [
        ("slack", notify_slack),
        ("teams", notify_teams),
        ("email", notify_email),
    ]:
        try:
            results[channel] = fn(report)
        except Exception:
            results[channel] = False

    return results
