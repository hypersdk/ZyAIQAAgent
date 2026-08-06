# Copyright 2026 ZyvorAI Labs Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Notification delivery — GitHub, Slack, Teams, Email."""

from __future__ import annotations

import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
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
    from github_integration.client import GitHubClient

    client = GitHubClient()
    body = f"{_status_emoji(report)} {report.summary}"
    if report.coverage_inventory_size is not None:
        body += "\n\n### Coverage"
        body += f"\n- Inventory: {report.coverage_inventory_size} candidate(s)"
        if report.coverage_gaps_remaining is not None:
            body += f"\n- Gaps remaining: {report.coverage_gaps_remaining}"
        if report.coverage_tests_generated is not None:
            body += f"\n- New coverage tests generated: {report.coverage_tests_generated}"
    if report.v8_coverage_percentage is not None:
        body += f"\n- V8 JS coverage: {report.v8_coverage_percentage}%"
    if report.failure_analysis:
        body += f"\n\n### Failure Analysis\n\n{report.failure_analysis}"
    if report.autofix_suggestions:
        body += "\n\n### Suggested Fixes\n"
        for suggestion in report.autofix_suggestions:
            body += f"- `{suggestion}`\n"
    if report.html_path:
        body += f"\n\n📄 Full report: `{report.html_path}`"
    if report.pdf_path:
        body += f"\n📑 PDF report: `{report.pdf_path}`"

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

    if report.pdf_path:
        pdf_file = Path(report.pdf_path)
        if pdf_file.is_file():
            with pdf_file.open("rb") as attachment:
                part = MIMEApplication(attachment.read(), _subtype="pdf")
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=pdf_file.name,
            )
            msg.attach(part)

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
