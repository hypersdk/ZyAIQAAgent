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

"""Offline tests for eval metrics and confidence scoring."""

from __future__ import annotations

from knowledge.citations import compute_confidence, validate_response
from knowledge.eval_metrics import (
    aggregate_report,
    groundedness_proxy,
    keyword_score,
    summarize_case_metrics,
)
from knowledge.schemas import Citation, QAResponse, SourceArtifact


def _artifact(document_id: str = "doc-1", score: float = 0.8) -> SourceArtifact:
    return SourceArtifact(
        document_id=document_id,
        title="Guide",
        source="customer-manual",
        section="Egress",
        url="https://example.invalid",
        product="PacketWolf",
        version="2.0",
        tenant_id="public",
        access_level="public",
        updated_at="2026-07-30",
        score=score,
        content="default deny",
    )


def test_keyword_and_groundedness_metrics() -> None:
    assert keyword_score("Use default-deny and DNS", ["default-deny", "DNS"]) == 1.0
    assert groundedness_proxy("answer", [{"document_id": "a"}, {"document_id": "b"}]) >= 0.7


def test_summarize_and_aggregate() -> None:
    case = {
        "expected_keywords": ["default-deny"],
        "expected_document_ids": ["doc-1"],
        "expect_abstain": False,
    }
    payload = {
        "answer": "Apply default-deny egress.",
        "citations": [{"document_id": "doc-1"}],
        "insufficient_context": False,
        "confidence": "high",
        "retrieval": {"validated_citations": 1, "documents_considered": 2},
    }
    metrics = summarize_case_metrics(case, payload)
    assert metrics["keyword_score"] == 1.0
    assert metrics["citation_precision"] == 1.0
    assert metrics["abstention_accuracy"] == 1.0

    report = aggregate_report(
        [{"status_code": 200, "has_citation": True, **metrics}],
        [0.5, 1.0],
    )
    assert report["http_success_rate"] == 1.0
    assert report["mean_keyword_score"] == 1.0


def test_compute_confidence_high_with_strong_evidence() -> None:
    conf, score = compute_confidence(
        artifacts=[_artifact(score=0.9)],
        validated_citations=[Citation(document_id="doc-1", title="Guide", source="manual")],
        insufficient_context=False,
    )
    assert conf == "high"
    assert score >= 0.72


def test_validate_response_overrides_inflated_model_confidence() -> None:
    response = QAResponse(
        answer="Maybe something.",
        confidence="high",
        citations=[Citation(document_id="doc-1", title="x", source="y")],
    )
    validated = validate_response(response, [_artifact(score=0.1)])
    assert validated.confidence in {"low", "medium"}
