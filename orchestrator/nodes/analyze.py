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

"""Analyze test failures."""

from __future__ import annotations

import os
from pathlib import Path

from agents.analyzer.agent import analyze_failures
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def analyze_failures_node(state: PipelineState) -> PipelineState:
    """Run failure analysis on test results with full artifact context."""
    test_results = state.get("test_results")
    if not test_results or test_results.all_passed:
        return {**state, "failure_analysis": None}

    use_llm = os.environ.get("ENABLE_LLM_ANALYSIS", "true").lower() == "true"
    artifact_dir = _repo_root() / "test-results"
    analysis = analyze_failures(test_results, artifact_dir=artifact_dir, use_llm=use_llm)
    return {**state, "failure_analysis": analysis}
