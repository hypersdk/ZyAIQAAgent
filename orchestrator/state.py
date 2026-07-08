"""Pipeline state shared across LangGraph nodes."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from agents.common.models import Requirement, TestResult


class PipelineState(TypedDict, total=False):
    source: str
    spec_paths: List[str]
    spec_contents: List[str]
    requirements: List[Requirement]
    generated_tests: List[str]
    test_results: Optional[TestResult]
    failure_analysis: Optional[str]
    report_path: Optional[str]
    report_summary: Optional[str]
    pr_number: Optional[int]
    repo_full_name: Optional[str]
    error: Optional[str]
    metadata: Dict[str, Any]
