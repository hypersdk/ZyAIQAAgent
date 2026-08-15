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

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx

from knowledge.eval_metrics import aggregate_report, summarize_case_metrics


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Evaluate a running Zyvor QA API")
    result.add_argument(
        "--dataset",
        type=Path,
        default=Path("eval/knowledge_questions.jsonl"),
    )
    result.add_argument("--base-url", default="http://localhost:8080")
    result.add_argument("--api-key")
    result.add_argument("--tenant-id", default="public")
    result.add_argument("--access-levels", default="public,customer")
    result.add_argument("--output", type=Path, default=Path("eval/knowledge_report.json"))
    result.add_argument(
        "--langsmith",
        action="store_true",
        help="Enable LangSmith tracing for the eval run (requires LANGSMITH_API_KEY)",
    )
    result.add_argument(
        "--fail-under-keyword",
        type=float,
        default=0.0,
        help="Exit non-zero if mean keyword score is below this threshold",
    )
    return result


def _enable_langsmith(enabled: bool) -> None:
    if not enabled:
        return
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGSMITH_TRACING", "true")
    if not (os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY")):
        raise SystemExit(
            "--langsmith requires LANGSMITH_API_KEY (or LANGCHAIN_API_KEY) in the environment"
        )
    os.environ.setdefault("LANGCHAIN_PROJECT", "zyvor-knowledge-eval")


def main() -> None:
    args = parser().parse_args()
    _enable_langsmith(args.langsmith)

    headers = {
        "X-Tenant-ID": args.tenant_id,
        "X-Access-Levels": args.access_levels,
    }
    if args.api_key:
        headers["X-API-Key"] = args.api_key

    cases = [
        json.loads(line)
        for line in args.dataset.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    results: list[dict[str, Any]] = []
    latencies: list[float] = []

    with httpx.Client(base_url=args.base_url, headers=headers, timeout=120) as client:
        for case in cases:
            started = time.perf_counter()
            response = client.post(
                "/v1/qa",
                json={
                    "question": case["question"],
                    "product": case.get("product"),
                    "document_type": case.get("document_type"),
                    "thread_id": f"eval-{case.get('id', len(results))}",
                },
            )
            latency = time.perf_counter() - started
            latencies.append(latency)

            payload = (
                response.json()
                if response.headers.get("content-type", "").startswith("application/json")
                else {}
            )
            metrics = summarize_case_metrics(case, payload if isinstance(payload, dict) else {})
            results.append(
                {
                    "id": case.get("id"),
                    "status_code": response.status_code,
                    "latency_seconds": round(latency, 4),
                    **metrics,
                    "response": payload,
                }
            )

    report = aggregate_report(results, latencies)
    report["langsmith"] = bool(args.langsmith)
    report["results"] = results

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = {key: value for key, value in report.items() if key != "results"}
    print(json.dumps(summary, indent=2))

    if args.fail_under_keyword and report["mean_keyword_score"] < args.fail_under_keyword:
        raise SystemExit(
            f"mean_keyword_score {report['mean_keyword_score']:.3f} "
            f"< --fail-under-keyword {args.fail_under_keyword}"
        )


if __name__ == "__main__":
    main()
