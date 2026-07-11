"""Collect V8 JS coverage from Playwright test artifacts."""

from __future__ import annotations

from agents.coverage.v8_report import collect_v8_coverage
from orchestrator.state import PipelineState


def collect_v8_coverage_node(state: PipelineState) -> PipelineState:
    """Aggregate V8 coverage written during test execution."""
    summary = collect_v8_coverage()
    metadata = dict(state.get("metadata", {}))
    if summary:
        metadata["v8_coverage_percentage"] = summary.percentage
        metadata["v8_coverage_used_bytes"] = summary.used_bytes
        metadata["v8_coverage_total_bytes"] = summary.total_bytes
    return {**state, "v8_coverage": summary, "metadata": metadata}
