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

"""Export per-job test results as CSV / HTML / Markdown / PDF, with errors surfaced."""

from __future__ import annotations

import csv
import io
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from agents.reporter.pdf import html_to_pdf


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def cases_to_csv(cases: list[dict[str, Any]]) -> str:
    """Flatten result cases into CSV text."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["title", "status", "browser", "duration_ms", "error", "console_errors", "network_errors", "video", "trace"]
    )
    for c in cases:
        writer.writerow(
            [
                c.get("title", ""),
                c.get("status", ""),
                c.get("browser", ""),
                c.get("duration_ms", ""),
                (c.get("error") or "").replace("\n", " ").strip(),
                " | ".join(c.get("console_logs", []) or []),
                " | ".join(c.get("network_errors", []) or []),
                c.get("video", "") or "",
                c.get("trace", "") or "",
            ]
        )
    return buffer.getvalue()


def _md_escape(text: Any) -> str:
    """Escape pipe/newline characters so a value is safe inside a Markdown table cell."""
    return str(text or "").replace("|", "\\|").replace("\n", " ").strip()


def _status_emoji(status: Any) -> str:
    s = str(status or "").lower().replace("_", "-")
    if s in ("ok", "passed", "pass", "true", "good"):
        return "✅"
    if s in ("warn", "warning", "needs-improvement"):
        return "⚠️"
    if s in ("fail", "failed", "false", "error", "poor"):
        return "❌"
    return "•"


def _md_header(title: str, target: str | None, extra_lines: list[str], *, ok: bool) -> list[str]:
    """Shared Markdown report header — title, generated-at, target, and a few summary lines."""
    return [
        f"# {'✅' if ok else '❌'} {title}",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
        f"**Target:** {target or '—'}  ",
        *[f"{line}  " for line in extra_lines],
        "",
    ]


def cases_to_markdown(meta: dict[str, Any], cases: list[dict[str, Any]]) -> str:
    """Render a Markdown report for a job's cases — pastes cleanly into GitHub/Slack/Notion."""
    passed = sum(1 for c in cases if c.get("status") == "passed")
    extra = [f"**Result:** {passed}/{len(cases)} passed"]
    if meta.get("duration_s") is not None:
        extra.append(f"**Duration:** {meta['duration_s']}s")
    lines = _md_header(
        f"{meta.get('kind', 'test').replace('_', ' ').title()} Report",
        meta.get("target"),
        extra,
        ok=(passed == len(cases)),
    )
    lines += ["| Status | Test | Browser | Duration | Error |", "|---|---|---|---|---|"]
    for c in cases:
        duration = f"{c['duration_ms']}ms" if c.get("duration_ms") is not None else "—"
        error = _md_escape(c.get("error"))
        if len(error) > 140:
            error = error[:140] + "…"
        lines.append(
            f"| {_status_emoji(c.get('status'))} {(c.get('status') or 'fail').upper()} "
            f"| {_md_escape(c.get('title'))} | {c.get('browser') or '—'} | {duration} | {error or '—'} |"
        )
    failures = [c for c in cases if c.get("status") != "passed"]
    if failures:
        lines += ["", "## Failure details", ""]
        for c in failures:
            lines.append(f"### {_md_escape(c.get('title'))}")
            if c.get("error"):
                lines += ["```", c["error"].strip(), "```", ""]
    return "\n".join(lines) + "\n"


def cases_to_html(meta: dict[str, Any], cases: list[dict[str, Any]]) -> str:
    """Render a standalone HTML report for a job's cases."""
    env = Environment(loader=FileSystemLoader(_repo_root() / "templates"), autoescape=True)
    template = env.get_template("job-report.html.j2")
    failures = [c for c in cases if c.get("status") != "passed"]
    return template.render(
        meta=meta,
        cases=cases,
        failures=failures,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )


def build_report_bundle(
    kind: str,
    cases: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, str]:
    """Write report.html / report.csv / report.pdf into a PVC-backed job dir.

    Returns a map of format → /reports-relative href. Prunes to the newest 30.
    """
    reports = _repo_root() / "reports" / "jobs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    job_dir = reports / f"{stamp}-{kind}"
    job_dir.mkdir(parents=True, exist_ok=True)

    meta = {"kind": kind, **summary}
    (job_dir / "report.csv").write_text(cases_to_csv(cases), encoding="utf-8")
    (job_dir / "report.md").write_text(cases_to_markdown(meta, cases), encoding="utf-8")
    html = cases_to_html(meta, cases)
    html_path = job_dir / "report.html"
    html_path.write_text(html, encoding="utf-8")

    hrefs = {
        "html": f"/reports/jobs/{job_dir.name}/report.html",
        "csv": f"/reports/jobs/{job_dir.name}/report.csv",
        "md": f"/reports/jobs/{job_dir.name}/report.md",
    }

    if os.environ.get("ENABLE_PDF_REPORT", "true").lower() == "true":
        pdf_path = html_to_pdf(html_path, job_dir / "report.pdf")
        if pdf_path:
            hrefs["pdf"] = f"/reports/jobs/{job_dir.name}/report.pdf"

    _prune(reports, 30)
    return hrefs


def _prune(root: Path, keep: int) -> None:
    import shutil

    for stale in sorted([d for d in root.iterdir() if d.is_dir()])[:-keep]:
        shutil.rmtree(stale, ignore_errors=True)


def audit_to_csv(checks: list[str], pages: list[dict[str, Any]]) -> str:
    """Flatten the pages × checks matrix into CSV."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["page", "title", "status"] + [f"{c}_status" for c in checks] + ["issues"])
    for p in pages:
        issues = []
        for c in checks:
            for issue in (p.get("checks", {}).get(c, {}) or {}).get("issues", []):
                issues.append(f"[{c}] {issue}")
        writer.writerow(
            [p.get("path", ""), p.get("title", ""), p.get("status", "")]
            + [(p.get("checks", {}).get(c, {}) or {}).get("status", "-") for c in checks]
            + [" | ".join(issues)]
        )
    return buffer.getvalue()


def flow_to_markdown(url: str, steps: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    passed = sum(1 for s in steps if s.get("status") == "passed")
    lines = _md_header("Flow Test Report", url, [f"**Steps:** {passed}/{len(steps)} passed"], ok=(passed == len(steps)))
    lines += ["| # | Status | Action | Description | Error |", "|---|---|---|---|---|"]
    for s in steps:
        error = _md_escape(s.get("error"))
        lines.append(
            f"| {s.get('n', '')} | {_status_emoji(s.get('status'))} {(s.get('status') or '').upper()} "
            f"| {_md_escape(s.get('action'))} | {_md_escape(s.get('desc'))} | {error or '—'} |"
        )
    return "\n".join(lines) + "\n"


def build_flow_bundle(url: str, steps: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, str]:
    """Write a flow report (step table + embedded journey video) as HTML/CSV/Markdown/PDF."""
    reports = _repo_root() / "reports" / "jobs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    job_dir = reports / f"{stamp}-flow"
    job_dir.mkdir(parents=True, exist_ok=True)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["step", "action", "description", "status", "error"])
    for s in steps:
        w.writerow([s.get("n"), s.get("action"), s.get("desc"), s.get("status"), (s.get("error") or "").replace("\n", " ")])
    (job_dir / "report.csv").write_text(buf.getvalue(), encoding="utf-8")
    (job_dir / "report.md").write_text(flow_to_markdown(url, steps, summary), encoding="utf-8")

    env = Environment(loader=FileSystemLoader(_repo_root() / "templates"), autoescape=True)
    html = env.get_template("flow-report.html.j2").render(
        url=url, steps=steps, summary=summary,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
    html_path = job_dir / "report.html"
    html_path.write_text(html, encoding="utf-8")

    hrefs = {
        "html": f"/reports/jobs/{job_dir.name}/report.html",
        "csv": f"/reports/jobs/{job_dir.name}/report.csv",
        "md": f"/reports/jobs/{job_dir.name}/report.md",
    }
    if os.environ.get("ENABLE_PDF_REPORT", "true").lower() == "true":
        pdf = html_to_pdf(html_path, job_dir / "report.pdf")
        if pdf:
            hrefs["pdf"] = f"/reports/jobs/{job_dir.name}/report.pdf"
    _prune(reports, 30)
    return hrefs


def checks_to_markdown(title: str, url: str, data: dict[str, Any]) -> str:
    checks = data.get("checks") or []
    failed = sum(1 for c in checks if not c.get("ok"))
    lines = _md_header(f"{title} Report", url, [f"**Checks:** {len(checks) - failed}/{len(checks)} passed"], ok=(failed == 0))
    lines += ["| Status | Check | Detail |", "|---|---|---|"]
    for c in checks:
        lines.append(f"| {_status_emoji(c.get('ok'))} | {_md_escape(c.get('name'))} | {_md_escape(c.get('detail'))} |")
    return "\n".join(lines) + "\n"


def build_checks_bundle(url: str, data: dict[str, Any], *, kind: str = "checks", title: str = "Checks") -> dict[str, str]:
    """Write a generic checks-table report (name/ok/detail rows) as HTML/CSV/Markdown/PDF."""
    reports = _repo_root() / "reports" / "jobs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    job_dir = reports / f"{stamp}-{kind}"
    job_dir.mkdir(parents=True, exist_ok=True)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["check", "ok", "detail"])
    for c in data.get("checks") or []:
        w.writerow([c.get("name"), c.get("ok"), c.get("detail")])
    (job_dir / "report.csv").write_text(buf.getvalue(), encoding="utf-8")
    (job_dir / "report.md").write_text(checks_to_markdown(title, url, data), encoding="utf-8")

    env = Environment(loader=FileSystemLoader(_repo_root() / "templates"), autoescape=True)
    html = env.get_template("checks-report.html.j2").render(
        url=url, data=data, title=title,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
    html_path = job_dir / "report.html"
    html_path.write_text(html, encoding="utf-8")

    hrefs = {
        "html": f"/reports/jobs/{job_dir.name}/report.html",
        "csv": f"/reports/jobs/{job_dir.name}/report.csv",
        "md": f"/reports/jobs/{job_dir.name}/report.md",
    }
    if os.environ.get("ENABLE_PDF_REPORT", "true").lower() == "true":
        pdf = html_to_pdf(html_path, job_dir / "report.pdf")
        if pdf:
            hrefs["pdf"] = f"/reports/jobs/{job_dir.name}/report.pdf"
    _prune(reports, 30)
    return hrefs


def build_realtime_bundle(url: str, data: dict[str, Any]) -> dict[str, str]:
    """Write a live-data report (WS/SSE/live-view checks) as HTML/CSV/Markdown/PDF."""
    reports = _repo_root() / "reports" / "jobs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    job_dir = reports / f"{stamp}-realtime"
    job_dir.mkdir(parents=True, exist_ok=True)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["check", "ok", "detail"])
    for c in data.get("checks") or []:
        w.writerow([c.get("name"), c.get("ok"), c.get("detail")])
    (job_dir / "report.csv").write_text(buf.getvalue(), encoding="utf-8")
    (job_dir / "report.md").write_text(checks_to_markdown("Live Data", url, data), encoding="utf-8")

    env = Environment(loader=FileSystemLoader(_repo_root() / "templates"), autoescape=True)
    html = env.get_template("realtime-report.html.j2").render(
        url=url, data=data,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
    html_path = job_dir / "report.html"
    html_path.write_text(html, encoding="utf-8")

    hrefs = {
        "html": f"/reports/jobs/{job_dir.name}/report.html",
        "csv": f"/reports/jobs/{job_dir.name}/report.csv",
        "md": f"/reports/jobs/{job_dir.name}/report.md",
    }
    if os.environ.get("ENABLE_PDF_REPORT", "true").lower() == "true":
        pdf = html_to_pdf(html_path, job_dir / "report.pdf")
        if pdf:
            hrefs["pdf"] = f"/reports/jobs/{job_dir.name}/report.pdf"
    _prune(reports, 30)
    return hrefs


def vitals_to_markdown(url: str, data: dict[str, Any]) -> str:
    metrics = data.get("metrics") or {}
    poor = sum(1 for m in metrics.values() if _status_emoji(m.get("grade")) == "❌")
    lines = _md_header("Core Web Vitals Report", url, [f"**Metrics measured:** {len(metrics)}"], ok=(poor == 0))
    lines += ["| Metric | Value | Grade |", "|---|---|---|"]
    for name, m in metrics.items():
        lines.append(f"| {_md_escape(name)} | {m.get('value')} | {_status_emoji(m.get('grade'))} {_md_escape(m.get('grade'))} |")
    return "\n".join(lines) + "\n"


def build_vitals_bundle(url: str, data: dict[str, Any]) -> dict[str, str]:
    """Write a Core Web Vitals report (metric grades + screenshot) as HTML/CSV/Markdown/PDF."""
    reports = _repo_root() / "reports" / "jobs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    job_dir = reports / f"{stamp}-vitals"
    job_dir.mkdir(parents=True, exist_ok=True)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["metric", "value", "grade"])
    for name, m in (data.get("metrics") or {}).items():
        w.writerow([name, m.get("value"), m.get("grade")])
    (job_dir / "report.csv").write_text(buf.getvalue(), encoding="utf-8")
    (job_dir / "report.md").write_text(vitals_to_markdown(url, data), encoding="utf-8")

    env = Environment(loader=FileSystemLoader(_repo_root() / "templates"), autoescape=True)
    html = env.get_template("vitals-report.html.j2").render(
        url=url, data=data,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
    html_path = job_dir / "report.html"
    html_path.write_text(html, encoding="utf-8")

    hrefs = {
        "html": f"/reports/jobs/{job_dir.name}/report.html",
        "csv": f"/reports/jobs/{job_dir.name}/report.csv",
        "md": f"/reports/jobs/{job_dir.name}/report.md",
    }
    if os.environ.get("ENABLE_PDF_REPORT", "true").lower() == "true":
        pdf = html_to_pdf(html_path, job_dir / "report.pdf")
        if pdf:
            hrefs["pdf"] = f"/reports/jobs/{job_dir.name}/report.pdf"
    _prune(reports, 30)
    return hrefs


def api_contract_to_markdown(url: str, mode: str, rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    failed = sum(1 for r in rows if not r.get("ok"))
    lines = _md_header(
        "API Contract Report", url, [f"**Requests:** {len(rows) - failed}/{len(rows)} passed"], ok=(failed == 0)
    )
    if mode == "spec":
        lines += ["| Status | Method | Path | HTTP | Schema errors | Latency |", "|---|---|---|---|---|---|"]
        for r in rows:
            errors = _md_escape(" | ".join(r.get("schema_errors") or []) or r.get("note", ""))
            latency = f"{r['latency_ms']}ms" if r.get("latency_ms") is not None else "—"
            lines.append(
                f"| {_status_emoji(r.get('ok'))} | {r.get('method', '')} | {_md_escape(r.get('path'))} "
                f"| {r.get('status', '')} | {errors or '—'} | {latency} |"
            )
    else:
        lines += ["| # | Status | Step | Method | Path | HTTP | Error | Latency |", "|---|---|---|---|---|---|---|---|"]
        for r in rows:
            latency = f"{r['latency_ms']}ms" if r.get("latency_ms") is not None else "—"
            lines.append(
                f"| {r.get('n', '')} | {_status_emoji(r.get('ok'))} | {_md_escape(r.get('desc'))} "
                f"| {r.get('method', '')} | {_md_escape(r.get('path'))} | {r.get('status', '')} "
                f"| {_md_escape(r.get('error')) or '—'} | {latency} |"
            )
    return "\n".join(lines) + "\n"


def build_api_contract_bundle(url: str, mode: str, rows: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, str]:
    """Write an API-contract report (endpoint/step table + schema violations) as HTML/CSV/Markdown/PDF."""
    reports = _repo_root() / "reports" / "jobs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    job_dir = reports / f"{stamp}-api-contract"
    job_dir.mkdir(parents=True, exist_ok=True)

    buf = io.StringIO()
    w = csv.writer(buf)
    if mode == "spec":
        w.writerow(["method", "path", "status", "ok", "schema_errors", "latency_ms"])
        for r in rows:
            w.writerow([r.get("method"), r.get("path"), r.get("status"), r.get("ok"),
                        " | ".join(r.get("schema_errors") or []) or r.get("note", ""), r.get("latency_ms")])
    else:
        w.writerow(["step", "desc", "method", "path", "status", "ok", "error", "latency_ms"])
        for r in rows:
            w.writerow([r.get("n"), r.get("desc"), r.get("method"), r.get("path"),
                        r.get("status"), r.get("ok"), r.get("error", ""), r.get("latency_ms")])
    (job_dir / "report.csv").write_text(buf.getvalue(), encoding="utf-8")
    (job_dir / "report.md").write_text(api_contract_to_markdown(url, mode, rows, summary), encoding="utf-8")

    env = Environment(loader=FileSystemLoader(_repo_root() / "templates"), autoescape=True)
    html = env.get_template("api-contract-report.html.j2").render(
        url=url, mode=mode, rows=rows, summary=summary,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
    html_path = job_dir / "report.html"
    html_path.write_text(html, encoding="utf-8")

    hrefs = {
        "html": f"/reports/jobs/{job_dir.name}/report.html",
        "csv": f"/reports/jobs/{job_dir.name}/report.csv",
        "md": f"/reports/jobs/{job_dir.name}/report.md",
    }
    if os.environ.get("ENABLE_PDF_REPORT", "true").lower() == "true":
        pdf = html_to_pdf(html_path, job_dir / "report.pdf")
        if pdf:
            hrefs["pdf"] = f"/reports/jobs/{job_dir.name}/report.pdf"
    _prune(reports, 30)
    return hrefs


def route_sweep_to_markdown(url: str, rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    failed = sum(1 for r in rows if _status_emoji(r.get("status")) == "❌")
    lines = _md_header("Route Sweep Report", url, [f"**Routes checked:** {len(rows)}"], ok=(failed == 0))
    lines += ["| Status | Route | Viewport | Diff % |", "|---|---|---|---|"]
    for r in rows:
        diff = r.get("diff")
        lines.append(
            f"| {_status_emoji(r.get('status'))} | {_md_escape(r.get('route'))} | {r.get('viewport', '')} "
            f"| {diff if diff is not None else '—'} |"
        )
    return "\n".join(lines) + "\n"


def build_route_sweep_bundle(url: str, rows: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, str]:
    """Write a route-sweep report (route × viewport matrix + thumbnails) as HTML/CSV/Markdown/PDF."""
    reports = _repo_root() / "reports" / "jobs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    job_dir = reports / f"{stamp}-route-sweep"
    job_dir.mkdir(parents=True, exist_ok=True)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["route", "viewport", "status", "diff_percent"])
    for r in rows:
        w.writerow([r.get("route"), r.get("viewport"), r.get("status"), r.get("diff")])
    (job_dir / "report.csv").write_text(buf.getvalue(), encoding="utf-8")
    (job_dir / "report.md").write_text(route_sweep_to_markdown(url, rows, summary), encoding="utf-8")

    env = Environment(loader=FileSystemLoader(_repo_root() / "templates"), autoescape=True)
    html = env.get_template("route-sweep-report.html.j2").render(
        url=url, rows=rows, summary=summary,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
    html_path = job_dir / "report.html"
    html_path.write_text(html, encoding="utf-8")

    hrefs = {
        "html": f"/reports/jobs/{job_dir.name}/report.html",
        "csv": f"/reports/jobs/{job_dir.name}/report.csv",
        "md": f"/reports/jobs/{job_dir.name}/report.md",
    }
    if os.environ.get("ENABLE_PDF_REPORT", "true").lower() == "true":
        pdf = html_to_pdf(html_path, job_dir / "report.pdf")
        if pdf:
            hrefs["pdf"] = f"/reports/jobs/{job_dir.name}/report.pdf"
    _prune(reports, 30)
    return hrefs


def audit_to_markdown(
    url: str, checks: list[str], pages: list[dict[str, Any]], summary: dict[str, Any]
) -> str:
    by_check = summary.get("byCheck", {}) or {}
    total_fail = sum(v.get("fail", 0) for v in by_check.values())
    total_warn = sum(v.get("warn", 0) for v in by_check.values())
    lines = _md_header(
        "Site Audit Report",
        url,
        [f"**Pages scanned:** {len(pages)}", f"**Failing checks:** {total_fail}", f"**Warnings:** {total_warn}"],
        ok=(total_fail == 0),
    )
    lines += [
        "| Page | Title | Status | " + " | ".join(c.title() for c in checks) + " | Issues |",
        "|---|---|---|" + "---|" * len(checks) + "---|",
    ]
    for p in pages:
        issues = []
        for c in checks:
            for issue in (p.get("checks", {}).get(c, {}) or {}).get("issues", []):
                issues.append(f"[{c}] {issue}")
        cell_statuses = " | ".join((p.get("checks", {}).get(c, {}) or {}).get("status", "-") for c in checks)
        issue_text = _md_escape(" ".join(issues))
        if len(issue_text) > 200:
            issue_text = issue_text[:200] + "…"
        lines.append(
            f"| {_md_escape(p.get('path'))} | {_md_escape(p.get('title'))} | {_status_emoji(p.get('status'))} "
            f"| {cell_statuses} | {issue_text or '—'} |"
        )
    return "\n".join(lines) + "\n"


def build_audit_bundle(
    url: str,
    checks: list[str],
    pages: list[dict[str, Any]],
    summary: dict[str, Any],
    findings: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    """Write audit report.html / report.csv / report.pdf into a PVC-backed dir."""
    from agents.reporter.attack_graph import build_mermaid_graph

    reports = _repo_root() / "reports" / "jobs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    job_dir = reports / f"{stamp}-audit"
    job_dir.mkdir(parents=True, exist_ok=True)

    (job_dir / "report.csv").write_text(audit_to_csv(checks, pages), encoding="utf-8")
    (job_dir / "report.md").write_text(audit_to_markdown(url, checks, pages, summary), encoding="utf-8")
    env = Environment(loader=FileSystemLoader(_repo_root() / "templates"), autoescape=True)
    html = env.get_template("audit-report.html.j2").render(
        url=url,
        checks=checks,
        pages=pages,
        summary=summary,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        mermaid_graph=build_mermaid_graph(findings or []),
    )
    html_path = job_dir / "report.html"
    html_path.write_text(html, encoding="utf-8")

    hrefs = {
        "html": f"/reports/jobs/{job_dir.name}/report.html",
        "csv": f"/reports/jobs/{job_dir.name}/report.csv",
        "md": f"/reports/jobs/{job_dir.name}/report.md",
    }
    if os.environ.get("ENABLE_PDF_REPORT", "true").lower() == "true":
        pdf_path = html_to_pdf(html_path, job_dir / "report.pdf")
        if pdf_path:
            hrefs["pdf"] = f"/reports/jobs/{job_dir.name}/report.pdf"

    _prune(reports, 30)
    return hrefs
