"""Apply autofix patches and optionally re-run tests."""

from __future__ import annotations

import os

from agents.autofix.apply import apply_autofix_patches
from orchestrator.state import PipelineState


def apply_autofix_node(state: PipelineState) -> PipelineState:
    """Patch test files from autofix suggestions when ENABLE_AUTOFIX_APPLY=true."""
    if os.environ.get("ENABLE_AUTOFIX_APPLY", "false").lower() != "true":
        return state

    suggestions = state.get("autofix_suggestions", [])
    if not suggestions:
        return state

    updated, patched_files = apply_autofix_patches(suggestions)
    metadata = dict(state.get("metadata", {}))
    metadata["autofix_patches_applied"] = len(patched_files)
    metadata["autofix_patched_files"] = patched_files
    if patched_files:
        metadata["autofix_retries"] = metadata.get("autofix_retries", 0) + 1

    return {
        **state,
        "autofix_suggestions": updated,
        "metadata": metadata,
    }
