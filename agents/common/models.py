"""Shared Pydantic models for the QA pipeline."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RequirementStep(BaseModel):
    action: str
    target: Optional[str] = None
    value: Optional[str] = None
    assertion: Optional[str] = None


class Requirement(BaseModel):
    id: str
    title: str
    description: str
    priority: str = "medium"
    steps: List[RequirementStep] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class TestCaseResult(BaseModel):
    title: str
    status: str
    duration_ms: float = 0
    browser: Optional[str] = None
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    trace_path: Optional[str] = None
    video_path: Optional[str] = None
    console_logs: List[str] = Field(default_factory=list)
    network_errors: List[str] = Field(default_factory=list)
    api_failures: List[str] = Field(default_factory=list)


class RegressionDiff(BaseModel):
    file: str
    status: str  # pass | fail | new_baseline
    diff_percent: float = 0.0
    diff_image_path: Optional[str] = None
    message: Optional[str] = None


class ApiValidationResult(BaseModel):
    url: str
    method: str = "GET"
    expected_status: int = 200
    actual_status: int = 0
    passed: bool = False
    error: Optional[str] = None


class LogIssue(BaseModel):
    test_title: str
    severity: str  # error | warning
    source: str  # console | network
    message: str


class TestResult(BaseModel):
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total: int = 0
    duration_ms: float = 0
    cases: List[TestCaseResult] = Field(default_factory=list)
    regression_diffs: List[RegressionDiff] = Field(default_factory=list)
    api_validations: List[ApiValidationResult] = Field(default_factory=list)
    log_issues: List[LogIssue] = Field(default_factory=list)
    raw_json: Optional[Dict[str, Any]] = None

    @property
    def all_passed(self) -> bool:
        regression_failed = any(d.status == "fail" for d in self.regression_diffs)
        api_failed = any(not v.passed for v in self.api_validations)
        log_failed = any(i.severity == "error" for i in self.log_issues)
        return (
            self.failed == 0
            and self.total > 0
            and not regression_failed
            and not api_failed
            and not log_failed
        )


class ParsedRequirements(BaseModel):
    source: str
    requirements: List[Requirement] = Field(default_factory=list)


class PipelineReport(BaseModel):
    summary: str
    passed: int
    failed: int
    total: int
    failure_analysis: Optional[str] = None
    autofix_suggestions: Optional[List[str]] = None
    html_path: Optional[str] = None


class AutofixSuggestion(BaseModel):
    test_title: str
    original_selector: str
    suggested_selector: str
    confidence: str = "medium"
    explanation: str = ""
