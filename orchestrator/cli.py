"""CLI entry point for Zyvor QA Agent."""

from __future__ import annotations

import warnings

warnings.filterwarnings("ignore", message=".*OpenSSL.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langgraph.*")

import os
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
            from github.client import normalize_github_spec_path

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
    graph = get_compiled_graph()
    state = _initial_state(
        source=source,
        spec=spec,
        pr_number=pr_number,
        expand_coverage=expand_coverage,
    )
    result = graph.invoke(state)

    if result.get("error"):
        typer.echo(f"Pipeline error: {result['error']}", err=True)
        if result.get("test_results"):
            tr = result["test_results"]
            typer.echo(
                f"Partial results: {tr.passed} passed, {tr.failed} failed",
                err=True,
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

    if test_results and test_results.failed > 0:
        raise typer.Exit(code=1)


@app.command()
def test() -> None:
    """Run Playwright tests only (skip parse/generate)."""
    _load_env()
    from agents.execution.runner import run_playwright

    base_url = os.environ.get("ZYVOR_BASE_URL", "https://zyvor.dev")
    repo_root = Path(__file__).resolve().parents[1]
    test_dirs = [str(repo_root / "tests" / "manual")]

    typer.echo(f"Running Playwright tests against {base_url}...")
    results = run_playwright(test_dirs=test_dirs, base_url=base_url)
    typer.echo(f"Results: {results.passed} passed, {results.failed} failed")

    if results.failed > 0:
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
        generated = create_and_generate(description, output_dir)
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
def serve(
    port: int = typer.Option(8080, help="Webhook server port"),
    host: str = typer.Option("0.0.0.0", help="Bind host"),
) -> None:
    """Start FastAPI webhook server for GitHub events."""
    _load_env()
    import uvicorn

    from orchestrator.webhook import create_app

    typer.echo(f"Starting webhook server on {host}:{port}")
    uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    app()


def main() -> None:
    app()
