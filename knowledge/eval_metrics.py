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

"""Offline-evaluable metrics for Zyvor knowledge QA answers."""

from __future__ import annotations

from typing import Any


def keyword_score(answer: str, expected: list[str]) -> float:
    if not expected:
        return 1.0
    lowered = answer.lower()
    return sum(1 for keyword in expected if keyword.lower() in lowered) / len(expected)


def citation_precision(citations: list[dict[str, Any]], allowed_ids: set[str] | None) -> float:
    """Fraction of returned citations that appear in the allow-list (when known)."""
    if not citations:
        return 0.0
    if not allowed_ids:
        # Without a gold set, treat non-empty citations as present.
        return 1.0 if all(c.get("document_id") for c in citations) else 0.0
    hits = sum(1 for c in citations if c.get("document_id") in allowed_ids)
    return hits / len(citations)


def abstention_accuracy(
    *,
    insufficient_context: bool,
    expect_abstain: bool | None,
) -> float | None:
    if expect_abstain is None:
        return None
    return 1.0 if bool(insufficient_context) == bool(expect_abstain) else 0.0


def groundedness_proxy(answer: str, citations: list[dict[str, Any]]) -> float:
    """Cheap proxy: answers with citations and non-empty text score higher."""
    if not answer.strip():
        return 0.0
    if not citations:
        return 0.15
    # Reward multiple distinct sources lightly.
    unique = len({c.get("document_id") for c in citations if c.get("document_id")})
    return min(1.0, 0.55 + 0.15 * unique)


def summarize_case_metrics(case: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    answer = str(payload.get("answer", ""))
    citations = list(payload.get("citations") or [])
    expected_keywords = list(case.get("expected_keywords") or [])
    allowed_ids = set(case.get("expected_document_ids") or [])
    expect_abstain = case.get("expect_abstain")

    return {
        "keyword_score": keyword_score(answer, expected_keywords),
        "citation_precision": citation_precision(citations, allowed_ids or None),
        "groundedness_proxy": groundedness_proxy(answer, citations),
        "abstention_accuracy": abstention_accuracy(
            insufficient_context=bool(payload.get("insufficient_context")),
            expect_abstain=expect_abstain if expect_abstain is None else bool(expect_abstain),
        ),
        "has_citation": bool(citations),
        "confidence": payload.get("confidence"),
        "insufficient_context": payload.get("insufficient_context"),
        "validated_citations": (payload.get("retrieval") or {}).get("validated_citations"),
        "documents_considered": (payload.get("retrieval") or {}).get("documents_considered"),
    }


def aggregate_report(results: list[dict[str, Any]], latencies: list[float]) -> dict[str, Any]:
    import statistics

    def mean(key: str) -> float:
        values = [float(item[key]) for item in results if item.get(key) is not None]
        return statistics.fmean(values) if values else 0.0

    abstain_vals = [item["abstention_accuracy"] for item in results if item.get("abstention_accuracy") is not None]

    return {
        "cases": len(results),
        "http_success_rate": (
            sum(1 for item in results if item.get("status_code") == 200) / max(len(results), 1)
        ),
        "citation_rate": (
            sum(1 for item in results if item.get("has_citation")) / max(len(results), 1)
        ),
        "mean_keyword_score": mean("keyword_score"),
        "mean_citation_precision": mean("citation_precision"),
        "mean_groundedness_proxy": mean("groundedness_proxy"),
        "mean_abstention_accuracy": (
            statistics.fmean(abstain_vals) if abstain_vals else None
        ),
        "p50_latency_seconds": statistics.median(latencies) if latencies else 0.0,
        "p95_latency_seconds": (
            statistics.quantiles(latencies, n=20)[18]
            if len(latencies) >= 20
            else (sorted(latencies)[int(0.95 * (len(latencies) - 1))] if latencies else 0.0)
        ),
    }
