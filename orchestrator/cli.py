"""CLI entry point for Zyvor QA Agent."""

from __future__ import annotations

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
    spec: Optional[Path] = None,
    pr_number: Optional[int] = None,
) -> PipelineState:
    spec_paths: list[str] = []
    if spec:
        spec_paths = [str(spec.resolve())]

    return {
        "source": source,
        "spec_paths": spec_paths,
        "spec_contents": [],
        "requirements": [],
        "generated_tests": [],
        "test_results": None,
        "failure_analysis": None,
        "report_path": None,
        "report_summary": None,
        "pr_number": pr_number,
        "repo_full_name": os.environ.get("ZYVOR_PRODUCT_REPO"),
        "error": None,
        "metadata": {},
    }


@app.command()
def run(
    source: str = typer.Option("local", help="Requirement source: local | github"),
    spec: Optional[Path] = typer.Option(None, help="Local spec file path"),
    pr_number: Optional[int] = typer.Option(None, help="PR number for GitHub comment"),
) -> None:
    """Run the full QA pipeline: fetch → parse → generate → execute → report → notify."""
    _load_env()
    graph = get_compiled_graph()
    state = _initial_state(source=source, spec=spec, pr_number=pr_number)
    result = graph.invoke(state)

    if result.get("error"):
        typer.echo(f"Pipeline error: {result['error']}", err=True)
        raise typer.Exit(code=1)

    test_results = result.get("test_results")
    if test_results:
        typer.echo(
            f"Results: {test_results.passed} passed, "
            f"{test_results.failed} failed, {test_results.total} total"
        )
    if result.get("report_path"):
        typer.echo(f"Report: {result['report_path']}")

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
    spec: Path = typer.Option(..., help="Spec file to parse and generate tests from"),
) -> None:
    """Parse spec and generate Playwright tests (no execution)."""
    _load_env()

    subgraph_nodes = ["fetch", "parse", "generate"]
    state = _initial_state(source="local", spec=spec)

    for node in subgraph_nodes:
        if node == "fetch":
            from orchestrator.nodes.fetch import fetch_requirements

            state = fetch_requirements(state)
        elif node == "parse":
            from orchestrator.nodes.parse import parse_requirements

            state = parse_requirements(state)
        elif node == "generate":
            from orchestrator.nodes.generate import generate_tests

            state = generate_tests(state)

    if state.get("error"):
        typer.echo(f"Error: {state['error']}", err=True)
        raise typer.Exit(code=1)

    generated = state.get("generated_tests", [])
    typer.echo(f"Generated {len(generated)} test file(s):")
    for path in generated:
        typer.echo(f"  {path}")


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
