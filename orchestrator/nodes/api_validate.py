"""API validation node."""

from __future__ import annotations

import os
from pathlib import Path

from agents.api_validation.validator import load_har_validations, validate_test_results
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def api_validate(state: PipelineState) -> PipelineState:
    """Validate API responses when ENABLE_API_VALIDATION=true."""
    if os.environ.get("ENABLE_API_VALIDATION", "false").lower() != "true":
        return state

    test_results = state.get("test_results")
    if not test_results:
        return state

    validations = validate_test_results(test_results)

    har_dir = _repo_root() / "traces"
    for har in har_dir.glob("*.har"):
        validations.extend(load_har_validations(har))

    test_results.api_validations = validations
    return {**state, "test_results": test_results, "api_validations": validations}
