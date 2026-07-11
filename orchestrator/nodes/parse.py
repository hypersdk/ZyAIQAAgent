"""Parse requirements from spec content."""

from __future__ import annotations

import os
from pathlib import Path

from agents.common.models import ParsedRequirements
from agents.coverage.gap import gaps_to_requirements
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

    coverage_gaps = state.get("coverage_gaps", [])
    if coverage_gaps:
        max_new = int(os.environ.get("COVERAGE_MAX_NEW_TESTS", "10"))
        gap_requirements = gaps_to_requirements(coverage_gaps[:max_new])
        existing_ids = {req.id for req in all_requirements}
        for req in gap_requirements:
            if req.id not in existing_ids:
                all_requirements.append(req)
                existing_ids.add(req.id)

    if not all_requirements and spec_contents:
        return {**state, "error": "No requirements extracted from specs"}

    if not all_requirements and not spec_contents and not coverage_gaps:
        return {**state, "error": "No requirements extracted from specs"}

    output_path = _repo_root() / "tests" / "fixtures" / "requirements.json"
    save_requirements(
        ParsedRequirements(source=source, requirements=all_requirements),
        output_path,
    )

    metadata = dict(state.get("metadata", {}))
    metadata["coverage_requirements_added"] = sum(
        1 for req in all_requirements if "coverage" in req.tags
    )

    return {**state, "requirements": all_requirements, "metadata": metadata}
