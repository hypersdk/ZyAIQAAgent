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

"""Parse requirements from spec content."""

from __future__ import annotations

import os
from pathlib import Path

from agents.common.models import ParsedRequirements
from agents.coverage.gap import gaps_to_requirements
from agents.parser.agent import parse_spec_content, save_requirements
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def parse_requirements(state: PipelineState) -> PipelineState:
    """Parse all spec contents into structured requirements."""
    if state.get("error"):
        return state

    spec_contents = state.get("spec_contents", [])
    spec_paths = state.get("spec_paths", [])
    source = state.get("source", "local")
    # Best-effort attribution of each requirement back to the file it came
    # from — only trustworthy when the two lists line up 1:1 (true for the
    # `document` source; the `github` source can skip a path that no longer
    # exists, which would misalign a strict zip, so origin_id is left unset
    # rather than risk mislabeling).
    origins = spec_paths if len(spec_paths) == len(spec_contents) else [None] * len(spec_contents)
    all_requirements = []

    for content, origin in zip(spec_contents, origins):
        try:
            parsed = parse_spec_content(content, source=source)
            for req in parsed.requirements:
                req.source_type = source
                req.origin_id = origin
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
