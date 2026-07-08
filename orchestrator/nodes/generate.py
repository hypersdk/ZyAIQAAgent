"""Generate Playwright tests from requirements."""

from __future__ import annotations

from pathlib import Path

from agents.generator.agent import generate_tests_from_requirements, render_template_fallback
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def generate_tests(state: PipelineState) -> PipelineState:
    """Generate Playwright test files."""
    if state.get("error"):
        return state

    requirements = state.get("requirements", [])
    if not requirements:
        return {**state, "generated_tests": []}

    output_dir = _repo_root() / "tests" / "generated"
    generated: list[str] = []

    try:
        generated = generate_tests_from_requirements(requirements, output_dir)
    except Exception:
        for req in requirements:
            path = render_template_fallback(req, output_dir)
            generated.append(path)

    return {**state, "generated_tests": generated}
