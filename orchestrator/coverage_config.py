"""Shared helpers for coverage expansion."""

from __future__ import annotations

import os

from orchestrator.state import PipelineState


def coverage_expansion_enabled(state: PipelineState) -> bool:
    """Return whether discovery/gap analysis should run."""
    if state.get("expand_coverage"):
        return True
    if state.get("metadata", {}).get("explicit_spec"):
        return False
    return os.environ.get("ENABLE_COVERAGE_EXPANSION", "false").lower() == "true"
