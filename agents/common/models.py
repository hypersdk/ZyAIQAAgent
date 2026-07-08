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
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    trace_path: Optional[str] = None


class TestResult(BaseModel):
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total: int = 0
    duration_ms: float = 0
    cases: List[TestCaseResult] = Field(default_factory=list)
    raw_json: Optional[Dict[str, Any]] = None

    @property
    def all_passed(self) -> bool:
        return self.failed == 0 and self.total > 0


class ParsedRequirements(BaseModel):
    source: str
    requirements: List[Requirement] = Field(default_factory=list)


class PipelineReport(BaseModel):
    summary: str
    passed: int
    failed: int
    total: int
    failure_analysis: Optional[str] = None
    html_path: Optional[str] = None
