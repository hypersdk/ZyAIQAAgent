"""Analyze test failures."""

from __future__ import annotations

import os
from pathlib import Path

from agents.analyzer.agent import analyze_failures
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def analyze_failures_node(state: PipelineState) -> PipelineState:
    """Run failure analysis on test results with full artifact context."""
    test_results = state.get("test_results")
    if not test_results or test_results.all_passed:
        return {**state, "failure_analysis": None}

    use_llm = os.environ.get("ENABLE_LLM_ANALYSIS", "true").lower() == "true"
    artifact_dir = _repo_root() / "test-results"
    analysis = analyze_failures(test_results, artifact_dir=artifact_dir, use_llm=use_llm)
    return {**state, "failure_analysis": analysis}
