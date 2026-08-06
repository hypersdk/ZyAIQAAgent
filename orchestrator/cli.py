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

"""CLI entry point for Zyvor QA Agent."""

from __future__ import annotations

import warnings

warnings.filterwarnings("ignore", message=".*OpenSSL.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langgraph.*")

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

from orchestrator.graph import get_compiled_graph
from orchestrator.state import PipelineState

app = typer.Typer(
    name="zyvor-qa",
    help="Zyvor QA Agent — autonomous Playwright testing for Zyvor platform",
    no_args_is_help=True,
)


def _load_env() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")


def _initial_state(
    source: str = "local",
    spec: Optional[str] = None,
    pr_number: Optional[int] = None,
    expand_coverage: bool = False,
) -> PipelineState:
    spec_paths: list[str] = []
    if spec:
        if source == "github":
            from github_integration.client import normalize_github_spec_path

            spec_paths = [normalize_github_spec_path(spec)]
        else:
            spec_paths = [str(Path(spec).resolve())]

    env_expand = os.environ.get("ENABLE_COVERAGE_EXPANSION", "false").lower() == "true"

    return {
        "source": source,
        "spec_paths": spec_paths,
        "spec_contents": [],
        "requirements": [],
        "generated_tests": [],
        "test_results": None,
        "failure_analysis": None,
        "report_path": None,
        "pdf_report_path": None,
        "report_summary": None,
        "pr_number": pr_number,
        "repo_full_name": os.environ.get("ZYVOR_PRODUCT_REPO"),
        "error": None,
        "metadata": {"explicit_spec": bool(spec)},
        "expand_coverage": expand_coverage or env_expand,
        "coverage_inventory": [],
        "coverage_gaps": [],
    }


def _run_discovery_subgraph(state: PipelineState) -> PipelineState:
    from orchestrator.nodes.discover import discover_coverage
    from orchestrator.nodes.fetch import fetch_requirements
    from orchestrator.nodes.gap_analyze import gap_analyze

    state = fetch_requirements(state)
    if state.get("error"):
        return state
    state = discover_coverage(state)
    return gap_analyze(state)


@app.command()
def run(
    source: str = typer.Option("local", help="Requirement source: local | github"),
    spec: Optional[str] = typer.Option(
        None,
        help="Spec path: local file, GitHub repo path (docs/specs/foo.md), or GitHub blob URL",
    ),
    pr_number: Optional[int] = typer.Option(None, help="PR number for GitHub comment"),
    expand_coverage: bool = typer.Option(
        False,
        "--expand-coverage",
        help="Discover routes/pages from GitHub code/docs and generate missing tests",
    ),
) -> None:
    """Run the full QA pipeline: fetch → parse → generate → execute → report → notify."""
    _load_env()
    t0 = time.time()
    started_at = datetime.fromtimestamp(t0, tz=timezone.utc).isoformat()
    graph = get_compiled_graph()
    state = _initial_state(
        source=source,
        spec=spec,
        pr_number=pr_number,
        expand_coverage=expand_coverage,
    )
    result = graph.invoke(state)

    from agents.reporter.summary import write_ci_summary

    base_url = os.environ.get("ZYVOR_BASE_URL")

    if result.get("error"):
        typer.echo(f"Pipeline error: {result['error']}", err=True)
        tr = result.get("test_results")
        if tr:
            typer.echo(
                f"Partial results: {tr.passed} passed, {tr.failed} failed",
                err=True,
            )
        write_ci_summary(
            command="run",
            target_url=base_url,
            passed=tr.passed if tr else 0,
            failed=tr.failed if tr else 0,
            total=tr.total if tr else 0,
            exit_code=1,
            started_at=started_at,
            duration_s=time.time() - t0,
            extra={"pipeline_error": result["error"]},
        )
        raise typer.Exit(code=1)

    test_results = result.get("test_results")
    metadata = result.get("metadata", {})
    if metadata.get("coverage_inventory_size") is not None:
        typer.echo(
            f"Coverage: {metadata.get('coverage_inventory_size', 0)} candidates, "
            f"{metadata.get('coverage_gaps_remaining', 0)} gaps, "
            f"{metadata.get('coverage_tests_generated', 0)} new tests"
        )
    if test_results:
        typer.echo(
            f"Results: {test_results.passed} passed, "
            f"{test_results.failed} failed, {test_results.total} total"
        )
        generated = result.get("generated_tests", [])
        if generated:
            typer.echo(f"Generated tests: {len(generated)} file(s)")
    if result.get("report_path"):
        typer.echo(f"Report: {result['report_path']}")
    if result.get("pdf_report_path"):
        typer.echo(f"PDF report: {result['pdf_report_path']}")

    failed = bool(test_results and test_results.failed > 0)
    write_ci_summary(
        command="run",
        target_url=base_url,
        passed=test_results.passed if test_results else 0,
        failed=test_results.failed if test_results else 0,
        total=test_results.total if test_results else 0,
        exit_code=1 if failed else 0,
        started_at=started_at,
        duration_s=time.time() - t0,
        artifacts={
            "report_html": result.get("report_path"),
            "report_pdf": result.get("pdf_report_path"),
        },
    )
    if failed:
        raise typer.Exit(code=1)


@app.command()
def test(
    grep: Optional[str] = typer.Option(None, help="Playwright --grep filter (e.g. @smoke)"),
    shard: Optional[str] = typer.Option(None, help="Playwright --shard i/n (e.g. 1/2)"),
) -> None:
    """Run Playwright tests only (skip parse/generate)."""
    _load_env()
    t0 = time.time()
    started_at = datetime.fromtimestamp(t0, tz=timezone.utc).isoformat()
    from agents.execution.runner import run_playwright
    from agents.reporter.summary import write_ci_summary

    base_url = os.environ.get("ZYVOR_BASE_URL", "https://zyvor.dev")
    repo_root = Path(__file__).resolve().parents[1]
    test_dirs = [str(repo_root / "tests" / "manual")]
    grep = grep or os.environ.get("ZYVOR_GREP")
    shard = shard or os.environ.get("ZYVOR_SHARD")

    extra = []
    if grep:
        extra.append(f"grep={grep}")
    if shard:
        extra.append(f"shard={shard}")
    typer.echo(f"Running Playwright tests against {base_url}" + (f" ({', '.join(extra)})" if extra else "") + "...")
    results = run_playwright(
        test_dirs=test_dirs,
        base_url=base_url,
        grep=grep,
        shard=shard,
    )
    typer.echo(f"Results: {results.passed} passed, {results.failed} failed")

    failed = results.failed > 0
    write_ci_summary(
        command="test",
        target_url=base_url,
        passed=results.passed,
        failed=results.failed,
        skipped=results.skipped,
        total=results.total,
        exit_code=1 if failed else 0,
        started_at=started_at,
        duration_s=time.time() - t0,
        artifacts={"raw_json": "reports/results.json"},
    )
    if failed:
        raise typer.Exit(code=1)


@app.command()
def generate(
    spec: Optional[str] = typer.Option(
        None,
        help="Spec path: local file, GitHub repo path (docs/specs/foo.md), or GitHub blob URL",
    ),
    source: str = typer.Option("local", help="Requirement source: local | github"),
    expand_coverage: bool = typer.Option(
        False,
        "--expand-coverage",
        help="Discover routes/pages from GitHub code/docs and generate missing tests",
    ),
) -> None:
    """Parse spec and generate Playwright tests (no execution)."""
    _load_env()

    subgraph_nodes = ["fetch", "discover", "gap_analyze", "parse", "generate"]
    state = _initial_state(source=source, spec=spec, expand_coverage=expand_coverage)

    for node in subgraph_nodes:
        if node == "fetch":
            from orchestrator.nodes.fetch import fetch_requirements

            state = fetch_requirements(state)
        elif node == "discover":
            from orchestrator.nodes.discover import discover_coverage

            state = discover_coverage(state)
        elif node == "gap_analyze":
            from orchestrator.nodes.gap_analyze import gap_analyze

            state = gap_analyze(state)
        elif node == "parse":
            from orchestrator.nodes.parse import parse_requirements

            state = parse_requirements(state)
        elif node == "generate":
            from orchestrator.nodes.generate import generate_tests

            state = generate_tests(state)

    if state.get("error"):
        typer.echo(f"Error: {state['error']}", err=True)
        raise typer.Exit(code=1)

    metadata = state.get("metadata", {})
    if metadata.get("coverage_inventory_size") is not None:
        typer.echo(
            f"Coverage: {metadata.get('coverage_inventory_size', 0)} candidates, "
            f"{metadata.get('coverage_gaps_remaining', 0)} gaps, "
            f"{metadata.get('coverage_tests_generated', 0)} new tests"
        )

    generated = state.get("generated_tests", [])
    typer.echo(f"Generated {len(generated)} test file(s):")
    for path in generated:
        typer.echo(f"  {path}")


@app.command()
def discover(
    source: str = typer.Option("github", help="Requirement source: local | github"),
    spec: Optional[str] = typer.Option(
        None,
        help="Optional spec path when fetching from GitHub",
    ),
    pr_number: Optional[int] = typer.Option(None, help="PR number for changed-file scoping"),
) -> None:
    """Discover coverage inventory and gaps without generating or running tests."""
    _load_env()
    state = _initial_state(
        source=source,
        spec=spec,
        pr_number=pr_number,
        expand_coverage=True,
    )
    state = _run_discovery_subgraph(state)

    if state.get("error"):
        typer.echo(f"Error: {state['error']}", err=True)
        raise typer.Exit(code=1)

    inventory = state.get("coverage_inventory", [])
    gaps = state.get("coverage_gaps", [])
    metadata = state.get("metadata", {})

    typer.echo(f"Discovered {len(inventory)} coverage candidate(s)")
    typer.echo(f"Uncovered gaps: {len(gaps)}")
    if metadata.get("discovered_paths"):
        typer.echo(f"Files scanned: {len(metadata['discovered_paths'])}")

    for gap in gaps[:20]:
        candidate = gap.candidate
        typer.echo(f"  [gap] {candidate.kind} {candidate.path} — {candidate.title}")
    if len(gaps) > 20:
        typer.echo(f"  ... and {len(gaps) - 20} more")


@app.command()
def create(
    description: str = typer.Argument(..., help="Natural language test description"),
    execute: bool = typer.Option(False, help="Run generated tests immediately"),
) -> None:
    """Create Playwright tests from natural language (Phase 4)."""
    _load_env()
    from agents.nl_create.agent import create_and_generate, create_from_natural_language
    from agents.parser.agent import save_requirements

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / "tests" / "generated"

    typer.echo(f"Creating test from: {description}")
    try:
        parsed = create_from_natural_language(description)
    except Exception as exc:
        typer.echo(f"NL parsing failed: {exc}", err=True)
        raise typer.Exit(code=1)

    save_requirements(parsed, repo_root / "tests" / "fixtures" / "requirements.json")

    try:
        generated = create_and_generate(description, str(output_dir))
    except Exception as exc:
        typer.echo(f"Test generation failed: {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Generated {len(generated)} test file(s):")
    for path in generated:
        typer.echo(f"  {path}")

    if execute:
        from agents.execution.runner import run_playwright

        results = run_playwright(test_dirs=[str(output_dir)])
        typer.echo(f"Results: {results.passed} passed, {results.failed} failed")
        if results.failed > 0:
            raise typer.Exit(code=1)


@app.command()
def regression(
    update_baselines: bool = typer.Option(False, help="Update screenshot baselines"),
) -> None:
    """Run visual regression check (Phase 2)."""
    _load_env()
    if update_baselines:
        os.environ["UPDATE_BASELINES"] = "true"
    os.environ["ENABLE_REGRESSION"] = "true"

    from orchestrator.nodes.regression import regression_check

    from agents.execution.runner import run_playwright

    base_url = os.environ.get("ZYVOR_BASE_URL", "https://zyvor.dev")
    repo_root = Path(__file__).resolve().parents[1]
    test_dirs = [str(repo_root / "tests" / "manual")]

    typer.echo("Running tests with screenshot capture...")
    test_results = run_playwright(test_dirs=test_dirs, base_url=base_url)

    state = regression_check({"test_results": test_results})
    diffs = state.get("regression_diffs", [])

    for d in diffs:
        status = "✓" if d.status == "pass" else "✗"
        typer.echo(f"  {status} {d.file}: {d.diff_percent}% — {d.message or d.status}")

    failed = [d for d in diffs if d.status == "fail"]
    if failed:
        raise typer.Exit(code=1)


@app.command()
def flow(
    url: str = typer.Argument(..., help="Base URL to run the journey against"),
    describe: Optional[str] = typer.Option(None, help="Journey in plain English"),
    steps: Optional[str] = typer.Option(None, help="Path to a file with one step per line"),
    video: bool = typer.Option(True, help="Record the journey as a video"),
    trace: bool = typer.Option(True, help="Capture a Playwright trace.zip (time-travel debugger)"),
    insecure: bool = typer.Option(False, help="Accept self-signed TLS"),
    username: Optional[str] = typer.Option(None, help="Login username (best-effort sign-in)"),
    password: Optional[str] = typer.Option(None, help="Login password"),
    session: Optional[str] = typer.Option(None, help="Reuse a saved session file (path or name under reports/artifacts/auth)"),
    browser: Optional[str] = typer.Option(None, help="Browser engine: chromium | firefox | webkit"),
    device: Optional[str] = typer.Option(None, help="Playwright device profile, e.g. 'iPhone 14'"),
    throttle: Optional[str] = typer.Option(None, help="Network throttle: 3g | offline"),
) -> None:
    """Drive a multi-step user journey and record it end-to-end as one video."""
    _load_env()
    t0 = time.time()
    started_at = datetime.fromtimestamp(t0, tz=timezone.utc).isoformat()
    import os as _os

    from agents.flow.engine import run_flow
    from agents.flow.parse import parse_flow
    from agents.reporter.summary import write_ci_summary

    if browser in ("chromium", "firefox", "webkit"):
        _os.environ["ZYVOR_BROWSER"] = browser
    if device:
        _os.environ["ZYVOR_DEVICE"] = device
    if throttle in ("3g", "offline"):
        _os.environ["ZYVOR_THROTTLE"] = throttle

    if steps:
        text, steps_mode = Path(steps).read_text(encoding="utf-8"), True
    elif describe:
        text, steps_mode = describe, False
    else:
        typer.echo("Provide --describe or --steps", err=True)
        raise typer.Exit(code=2)

    parsed, mode = parse_flow(text, steps_mode=steps_mode)
    typer.echo(f"{len(parsed)} step(s) parsed ({mode})")
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "reports" / "artifacts" / "flows" / "cli"
    session_path = ""
    if session:
        cand = Path(session)
        if not cand.exists():
            cand = repo_root / "reports" / "artifacts" / "auth" / session
        session_path = str(cand) if cand.exists() else ""
        if session_path:
            typer.echo(f"reusing session {session_path}")
    result = run_flow(
        url, parsed, out_dir, record=video, trace=trace, insecure=insecure,
        username=username or "", password=password or "", session=session_path,
        on_line=lambda line: typer.echo(line),
    )
    typer.echo(f"Result: {result['passed']}/{result['total']} steps passed")
    if result.get("video"):
        typer.echo(f"Journey video: {out_dir / result['video']}")
    if result.get("trace"):
        typer.echo(f"Trace (open at trace.playwright.dev): {out_dir / result['trace']}")
    failed = result["failed"] > 0
    write_ci_summary(
        command="flow",
        target_url=url,
        passed=result["passed"],
        failed=result["failed"],
        total=result["total"],
        exit_code=1 if failed else 0,
        started_at=started_at,
        duration_s=time.time() - t0,
        artifacts={
            "video": str(out_dir / result["video"]) if result.get("video") else None,
            "trace": str(out_dir / result["trace"]) if result.get("trace") else None,
        },
    )
    if failed:
        raise typer.Exit(code=1)


@app.command(name="route-sweep")
def route_sweep(
    url: str = typer.Argument(..., help="Base URL"),
    routes: str = typer.Option("/", help="Comma-separated routes to screenshot"),
    mobile: bool = typer.Option(False, help="Also capture mobile viewport"),
    update_baselines: bool = typer.Option(False, help="Capture/replace baselines"),
    auto: bool = typer.Option(False, help="Auto-discover routes by crawling the site"),
    max_pages: int = typer.Option(20, help="Max routes to discover when --auto"),
    insecure: bool = typer.Option(False, help="Accept self-signed TLS"),
) -> None:
    """Screenshot a list of routes and diff against baselines."""
    _load_env()
    t0 = time.time()
    started_at = datetime.fromtimestamp(t0, tz=timezone.utc).isoformat()
    from orchestrator.dashboard.jobs import _job_route_sweep
    from agents.reporter.summary import write_ci_summary

    vps = ["desktop"] + (["mobile"] if mobile else [])
    result = _job_route_sweep({
        "url": url,
        "routes": [r.strip() for r in routes.split(",") if r.strip()],
        "viewports": vps,
        "update_baselines": update_baselines,
        "insecure": insecure,
        "auto": auto,
        "max_pages": max_pages,
    })
    typer.echo(f"Swept {result['routes']} route(s): {result['fail_count']} changed, {result['new_baselines']} new baseline(s)")
    for row in result["sweep_rows"]:
        typer.echo(f"  {row['status']:8} {row['route']} [{row['viewport']}] {row['diff']}%")

    fail_count = result["fail_count"]
    total_rows = len(result["sweep_rows"])
    write_ci_summary(
        command="route-sweep",
        target_url=url,
        passed=total_rows - fail_count,
        failed=fail_count,
        total=total_rows,
        exit_code=1 if fail_count > 0 else 0,
        started_at=started_at,
        duration_s=time.time() - t0,
        artifacts={"report_html": (result.get("report") or {}).get("html")},
        extra={"new_baselines": result["new_baselines"], "routes": result["routes"]},
    )
    if fail_count > 0:
        raise typer.Exit(code=1)


@app.command(name="api-test")
def api_test(
    base: str = typer.Argument(..., help="API base URL"),
    spec: Optional[str] = typer.Option(None, help="OpenAPI spec URL or local JSON file"),
    workflow: Optional[str] = typer.Option(None, help="JSON file with an ordered workflow of steps"),
    include_writes: bool = typer.Option(False, help="Also exercise POST/PUT/PATCH/DELETE endpoints"),
    token: Optional[str] = typer.Option(None, help="Bearer token for auth"),
    api_key: Optional[str] = typer.Option(None, help="API key (sent as x-api-key)"),
    insecure: bool = typer.Option(False, help="Accept self-signed TLS"),
) -> None:
    """Validate REST endpoints against their OpenAPI schema, or run an API workflow."""
    _load_env()
    import json as _json

    from orchestrator.dashboard.jobs import _job_api_contract

    spec_val = None
    if spec:
        if spec.startswith(("http://", "https://")):
            spec_val = spec
        else:
            spec_val = _json.loads(Path(spec).read_text(encoding="utf-8"))
    wf = _json.loads(Path(workflow).read_text(encoding="utf-8")) if workflow else None
    auth = {}
    if token:
        auth["token"] = token
    if api_key:
        auth["apiKey"] = api_key

    result = _job_api_contract({
        "url": base,
        "mode": "workflow" if wf else "spec",
        "spec": spec_val,
        "workflow": wf,
        "auth": auth or None,
        "include_writes": include_writes,
        "insecure": insecure,
        "max_endpoints": 200,
        "path_params": None,
    })
    typer.echo(f"API contract ({result['mode']}): {result['passed']}/{result['total']} passed")
    rows = result.get("endpoints") if result["mode"] == "spec" else result.get("steps")
    for r in rows or []:
        mark = "✓" if r.get("ok") else "✗"
        label = f"{r.get('method')} {r.get('path')}" if result["mode"] == "spec" else r.get("desc")
        detail = " | ".join(r.get("schema_errors") or []) or r.get("error") or r.get("note") or ""
        typer.echo(f"  {mark} {label} → {r.get('status')} {detail}")
    if result["failed"] > 0:
        raise typer.Exit(code=1)


@app.command(name="ai-test")
def ai_test(
    url: str = typer.Argument(..., help="App URL to drive"),
    goal: str = typer.Option(..., "--goal", "-g", help="Plain-English goal, e.g. 'create a ubuntu vm 1 vcpu 2gb ram'"),
    session: Optional[str] = typer.Option(None, help="Reuse a saved session (name under reports/artifacts/auth)"),
    max_steps: int = typer.Option(20, help="Max agent steps"),
    insecure: bool = typer.Option(False, help="Accept self-signed TLS"),
) -> None:
    """Autonomous AI tester — describe a goal and the agent drives the browser to do it."""
    _load_env()
    from orchestrator.dashboard.jobs import _job_ai_flow

    result = _job_ai_flow({"url": url, "goal": goal, "session": session or "",
                           "max_steps": max_steps, "insecure": insecure})
    typer.echo(f"\nAI agent ({result.get('mode')}): {'✅ ' + result['summary'] if result['success'] else '⚠ ' + result['summary']}")
    for s in result.get("ai_steps", []):
        mark = "✓" if s["status"] == "passed" else "✗"
        typer.echo(f"  {mark} step {s['n']}: {s['desc']}")
    if not result["success"]:
        raise typer.Exit(code=1)


@app.command(name="auth-test")
def auth_test(
    base: str = typer.Argument(..., help="App base URL"),
    login_url: Optional[str] = typer.Option(None, help="Login page path to drive in-browser"),
    api_login: Optional[str] = typer.Option(None, help="API login endpoint to POST credentials to"),
    protected: str = typer.Option("/", help="A protected path that requires auth"),
    logout_url: Optional[str] = typer.Option(None, help="Logout endpoint (to test session clearing)"),
    username: Optional[str] = typer.Option(None, help="Login username"),
    password: Optional[str] = typer.Option(None, help="Login password"),
    save_session: bool = typer.Option(True, help="Save the session for reuse by flow/realtime"),
    insecure: bool = typer.Option(False, help="Accept self-signed TLS"),
) -> None:
    """Log in, capture a reusable session, and assert auth/session behaviour."""
    _load_env()
    from orchestrator.dashboard.jobs import _job_auth_test

    result = _job_auth_test({
        "url": base, "login_url": login_url or "", "api_login": api_login or "",
        "protected": protected, "logout_url": logout_url or "",
        "username": username or "", "password": password or "",
        "save_session": save_session, "insecure": insecure,
    })
    typer.echo(f"Auth & session: {result['passed']}/{result['total']} checks passed")
    for c in result.get("checks") or []:
        typer.echo(f"  {'✓' if c['ok'] else '✗'} {c['name']} — {c.get('detail', '')}")
    if result.get("session_name"):
        typer.echo(f"Session saved as: {result['session_name']} (reuse with flow/realtime --session)")
    if result["failed"] > 0:
        raise typer.Exit(code=1)


@app.command(name="har-replay")
def har_replay(
    url: str = typer.Argument(..., help="Base URL"),
    mode: str = typer.Option("replay", help="record | replay"),
    har: Optional[str] = typer.Option(None, help="HAR file path (required for replay; default out dir for record)"),
    routes: Optional[str] = typer.Option("/", help="Comma/newline list of paths to visit when recording"),
    expect_text: Optional[str] = typer.Option(None, help="Text that must appear during replay"),
    not_found_ok: bool = typer.Option(False, help="On replay, fall back to network if a route is missing from HAR"),
    insecure: bool = typer.Option(False, help="Accept self-signed TLS"),
) -> None:
    """Record network traffic as HAR, or replay a page against a HAR file."""
    _load_env()
    from orchestrator.dashboard.jobs import _job_har_replay

    result = _job_har_replay({
        "url": url,
        "mode": mode,
        "har": har or os.environ.get("ZYVOR_HAR_PATH") or "",
        "routes": routes or "/",
        "expect_text": expect_text or "",
        "not_found_ok": not_found_ok,
        "insecure": insecure,
    })
    typer.echo(f"HAR {result.get('mode')}: {result['passed']}/{result['total']} checks")
    if result.get("har"):
        typer.echo(f"HAR file: {result['har']}")
    for c in result.get("checks") or []:
        typer.echo(f"  {'✓' if c['ok'] else '✗'} {c['name']} — {c.get('detail', '')}")
    if result["failed"] > 0:
        raise typer.Exit(code=1)


@app.command(name="import-codegen")
def import_codegen_cmd(
    source: str = typer.Argument(..., help="Path to a Playwright codegen .js/.ts file, or '-' for stdin"),
    url: Optional[str] = typer.Option(None, help="Base URL (required with --run)"),
    run: bool = typer.Option(False, help="Run the imported steps as a flow test"),
    insecure: bool = typer.Option(False, help="Accept self-signed TLS"),
) -> None:
    """Parse Playwright codegen output into flow steps (optionally run them)."""
    _load_env()
    if source == "-":
        script = sys.stdin.read()
    else:
        script = Path(source).read_text(encoding="utf-8")
    from orchestrator.dashboard.jobs import _job_import_codegen

    result = _job_import_codegen({
        "script": script,
        "url": url or "",
        "run": run,
        "insecure": insecure,
    })
    steps = result.get("imported_steps") or result.get("steps") or []
    typer.echo(f"Imported {len(steps)} step(s)")
    for i, s in enumerate(steps, 1):
        typer.echo(f"  {i}. {s.get('action')} {s.get('target') or s.get('assertion') or s.get('value') or ''}")
    if run and result.get("failed", 0) > 0:
        raise typer.Exit(code=1)


@app.command()
def realtime(
    url: str = typer.Argument(..., help="App base URL"),
    ws: Optional[str] = typer.Option(None, help="WebSocket path or full ws(s):// URL"),
    sse: Optional[str] = typer.Option(None, help="SSE endpoint path"),
    ticket_url: Optional[str] = typer.Option(None, help="One-time WS-ticket issue endpoint"),
    token: Optional[str] = typer.Option(None, help="Auth token (Bearer/subprotocol/query)"),
    subprotocol_jwt: bool = typer.Option(False, help="Send token via Sec-WebSocket-Protocol: <name>,<jwt>"),
    ws_subprotocol: str = typer.Option("access_token", help="WS subprotocol name (packetwolf: access_token, zeus-os: zeus-os-auth)"),
    token_query: str = typer.Option("token", help="Query-param name for the token (zeus-os: zeus_os_token)"),
    expect_messages: int = typer.Option(1, help="Minimum messages expected in the window"),
    window_ms: int = typer.Option(15000, help="Observation window (ms)"),
    live_selector: Optional[str] = typer.Option(None, help="CSS selector of a live region to watch for updates"),
    session: Optional[str] = typer.Option(None, help="Reuse a saved session (name under reports/artifacts/auth)"),
    insecure: bool = typer.Option(False, help="Accept self-signed TLS"),
) -> None:
    """Assert WebSocket/SSE streams are live and dashboard live regions update."""
    _load_env()
    from orchestrator.dashboard.jobs import _job_realtime

    result = _job_realtime({
        "url": url, "ws": ws or "", "sse": sse or "", "ticket_url": ticket_url or "",
        "ticket_query": "ticket", "token": token or "", "token_query": token_query,
        "ws_subprotocol": ws_subprotocol, "subprotocol_jwt": subprotocol_jwt,
        "expect_messages": expect_messages, "window_ms": window_ms,
        "live_selector": live_selector or "", "session": session or "", "insecure": insecure,
    })
    typer.echo(f"Live data: {result['passed']}/{result['total']} checks passed")
    for c in result.get("checks") or []:
        typer.echo(f"  {'✓' if c['ok'] else '✗'} {c['name']} — {c.get('detail', '')}")
    if result["failed"] > 0:
        raise typer.Exit(code=1)


@app.command()
def vitals(
    url: str = typer.Argument(..., help="URL to measure"),
    device: Optional[str] = typer.Option(None, help="Playwright device profile, e.g. 'iPhone 14'"),
    throttle: Optional[str] = typer.Option(None, help="Network throttle: 3g | offline"),
    insecure: bool = typer.Option(False, help="Accept self-signed TLS"),
) -> None:
    """Measure Core Web Vitals (LCP/CLS/INP/FCP/TTFB) and grade them."""
    _load_env()
    t0 = time.time()
    started_at = datetime.fromtimestamp(t0, tz=timezone.utc).isoformat()
    from orchestrator.dashboard.jobs import _job_vitals
    from agents.reporter.summary import write_ci_summary

    result = _job_vitals({"url": url, "device": device or "", "throttle": throttle or "", "insecure": insecure})
    typer.echo(f"Overall: {result.get('overall', '?').upper()}")
    metrics = result.get("metrics") or {}
    for name, m in metrics.items():
        typer.echo(f"  {name:5} {str(m.get('value')):>8}  [{m.get('grade')}]")

    total = len(metrics)
    passed = sum(1 for m in metrics.values() if m.get("grade") == "good")
    failed = total - passed
    write_ci_summary(
        command="vitals",
        target_url=url,
        passed=passed,
        failed=failed,
        total=total,
        exit_code=1 if failed > 0 else 0,
        started_at=started_at,
        duration_s=time.time() - t0,
        artifacts={"report_html": (result.get("report") or {}).get("html")},
        extra={"overall": result.get("overall"), "metrics": metrics},
    )
    if failed > 0:
        raise typer.Exit(code=1)


@app.command()
def serve(
    port: int = typer.Option(8080, help="Webhook server port"),
    host: str = typer.Option("0.0.0.0", help="Bind host"),  # nosec B104 - server must be externally reachable in Docker/K8s
    tls: bool = typer.Option(False, help="Serve over HTTPS (generates a self-signed cert if none given)"),
    tls_cert: Optional[str] = typer.Option(None, help="Path to a TLS certificate (PEM)"),
    tls_key: Optional[str] = typer.Option(None, help="Path to the TLS private key (PEM)"),
) -> None:
    """Start FastAPI webhook server for GitHub events + Mission Control dashboard."""
    _load_env()
    import uvicorn

    from orchestrator.webhook import create_app

    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    if tls or tls_cert or tls_key:
        ssl_certfile, ssl_keyfile = _ensure_tls_cert(tls_cert, tls_key, host)
        typer.echo(f"Starting HTTPS server on {host}:{port} (cert: {ssl_certfile})")
    else:
        typer.echo(f"Starting webhook server on {host}:{port}")
    uvicorn.run(create_app(), host=host, port=port, ssl_certfile=ssl_certfile, ssl_keyfile=ssl_keyfile)


def _ensure_tls_cert(cert: Optional[str], key: Optional[str], host: str) -> tuple[str, str]:
    """Return (cert_path, key_path); generate a self-signed pair if not provided."""
    import subprocess

    if cert and key:
        return cert, key
    cert_dir = Path.home() / ".zyvor-qa" / "tls"
    cert_dir.mkdir(parents=True, exist_ok=True)
    cert_path, key_path = cert_dir / "server.crt", cert_dir / "server.key"
    if cert_path.exists() and key_path.exists():
        return str(cert_path), str(key_path)
    cn = host if host not in ("0.0.0.0", "") else "localhost"  # nosec B104 - cert CN choice, not a bind address
    typer.echo(f"Generating self-signed TLS certificate (CN={cn}) → {cert_dir}")
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", str(key_path), "-out", str(cert_path),
            "-days", "825", "-subj", f"/CN={cn}",
            "-addext", f"subjectAltName=DNS:{cn},DNS:localhost,IP:127.0.0.1",
        ],
        check=True, capture_output=True,
    )
    return str(cert_path), str(key_path)


@app.command("knowledge-ingest")
def knowledge_ingest(
    path: Path = typer.Argument(..., help="File or directory to ingest"),
    tenant_id: str = typer.Option("public", "--tenant-id"),
    access_level: str = typer.Option("public", "--access-level"),
    product: Optional[str] = typer.Option(None, "--product"),
    source: str = typer.Option("documentation", "--source"),
    chunk_size: int = typer.Option(1400, "--chunk-size"),
    chunk_overlap: int = typer.Option(180, "--chunk-overlap"),
    batch_size: int = typer.Option(64, "--batch-size"),
) -> None:
    """Ingest docs into the Zyvor knowledge Qdrant collection (requires [knowledge])."""
    _load_env()
    try:
        from scripts.knowledge_ingest import main as ingest_main
    except ImportError as exc:
        typer.echo(
            "Knowledge extras missing. Install with: pip install -e '.[knowledge]'",
            err=True,
        )
        raise typer.Exit(code=1) from exc

    import sys

    argv = [
        str(path),
        "--tenant-id",
        tenant_id,
        "--access-level",
        access_level,
        "--source",
        source,
        "--chunk-size",
        str(chunk_size),
        "--chunk-overlap",
        str(chunk_overlap),
        "--batch-size",
        str(batch_size),
    ]
    if product:
        argv.extend(["--product", product])
    sys.argv = ["knowledge-ingest", *argv]
    ingest_main()


@app.command("knowledge-evaluate")
def knowledge_evaluate(
    base_url: str = typer.Option("http://localhost:8080", "--base-url"),
    api_key: Optional[str] = typer.Option(None, "--api-key"),
    tenant_id: str = typer.Option("public", "--tenant-id"),
    dataset: Path = typer.Option(
        Path("eval/knowledge_questions.jsonl"), "--dataset"
    ),
    output: Path = typer.Option(Path("eval/knowledge_report.json"), "--output"),
) -> None:
    """Evaluate a running knowledge QA API against the sample dataset."""
    _load_env()
    import sys

    from scripts.knowledge_evaluate import main as evaluate_main

    argv = [
        "--base-url",
        base_url,
        "--tenant-id",
        tenant_id,
        "--dataset",
        str(dataset),
        "--output",
        str(output),
    ]
    if api_key:
        argv.extend(["--api-key", api_key])
    sys.argv = ["knowledge-evaluate", *argv]
    evaluate_main()


if __name__ == "__main__":
    app()


def main() -> None:
    app()

