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

"""Persist and load QA run history for the dashboard."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.common.models import PipelineReport

MAX_HISTORY_FILES = 200


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def _history_dir() -> Path:
    return _repo_root() / "reports" / "history"


def append_run(report: PipelineReport, *, source: str = "local", duration_s: float | None = None) -> Path:
    """Write one history entry for a completed pipeline run."""
    history_dir = _history_dir()
    history_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc)
    entry = {
        "timestamp": timestamp.isoformat(),
        "source": source,
        "duration_s": round(duration_s, 1) if duration_s is not None else None,
        **report.model_dump(),
    }

    path = history_dir / f"run-{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    path.write_text(json.dumps(entry, indent=2), encoding="utf-8")
    _prune(history_dir)
    return path


def _prune(history_dir: Path) -> None:
    files = sorted(history_dir.glob("run-*.json"))
    for stale in files[:-MAX_HISTORY_FILES]:
        try:
            stale.unlink()
        except OSError:
            continue


def record_test_results(cases: list[dict[str, Any]]) -> None:
    """Append per-test pass/fail rows to a bounded index for trend analysis."""
    if not cases:
        return
    index = _repo_root() / "reports" / "test-index.jsonl"
    index.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    lines = []
    for c in cases:
        title = c.get("title")
        if not title:
            continue
        lines.append(json.dumps({"t": ts, "title": title, "status": c.get("status", "unknown")}))
    if not lines:
        return
    with index.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    # bound the file to the most recent ~5000 rows
    try:
        content = index.read_text(encoding="utf-8").splitlines()
        if len(content) > 5000:
            index.write_text("\n".join(content[-5000:]) + "\n", encoding="utf-8")
    except OSError:
        pass


def test_health(limit: int = 40) -> list[dict[str, Any]]:
    """Aggregate the per-test index: runs, fails, flake rate, last failure."""
    index = _repo_root() / "reports" / "test-index.jsonl"
    if not index.exists():
        return []
    agg: dict[str, dict[str, Any]] = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        title = row.get("title")
        if not title:
            continue
        rec = agg.setdefault(title, {"title": title, "runs": 0, "fails": 0, "last_fail": None})
        rec["runs"] += 1
        if row.get("status") != "passed":
            rec["fails"] += 1
            rec["last_fail"] = row.get("t")
    out = []
    for rec in agg.values():
        rec["fail_pct"] = round(100 * rec["fails"] / rec["runs"]) if rec["runs"] else 0
        rec["flaky"] = 0 < rec["fails"] < rec["runs"]
        out.append(rec)
    out.sort(key=lambda r: (-r["fails"], -r["fail_pct"]))
    return out[:limit]


def load_runs(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent runs, newest first."""
    history_dir = _history_dir()
    if not history_dir.exists():
        return []

    runs: list[dict[str, Any]] = []
    for path in sorted(history_dir.glob("run-*.json"), reverse=True)[:limit]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        runs.append(
            {
                "timestamp": data.get("timestamp"),
                "source": data.get("source", "unknown"),
                "passed": data.get("passed", 0),
                "failed": data.get("failed", 0),
                "total": data.get("total", 0),
                "duration_s": data.get("duration_s"),
                "summary": (data.get("summary") or "")[:300],
                "v8_coverage_percentage": data.get("v8_coverage_percentage"),
            }
        )
    return runs
