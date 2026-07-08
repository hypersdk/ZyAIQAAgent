"""Parse requirements from spec content."""

from __future__ import annotations

from pathlib import Path

from agents.common.models import ParsedRequirements
from agents.parser.agent import parse_spec_content, save_requirements
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_requirements(state: PipelineState) -> PipelineState:
    """Parse all spec contents into structured requirements."""
    if state.get("error"):
        return state

    spec_contents = state.get("spec_contents", [])
    source = state.get("source", "local")
    all_requirements = []

    for content in spec_contents:
        try:
            parsed = parse_spec_content(content, source=source)
            all_requirements.extend(parsed.requirements)
        except Exception as exc:
            return {**state, "error": f"Failed to parse requirements: {exc}"}

    if not all_requirements and spec_contents:
        return {**state, "error": "No requirements extracted from specs"}

    output_path = _repo_root() / "tests" / "fixtures" / "requirements.json"
    save_requirements(
        ParsedRequirements(source=source, requirements=all_requirements),
        output_path,
    )

    return {**state, "requirements": all_requirements}
