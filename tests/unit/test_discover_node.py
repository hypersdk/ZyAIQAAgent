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

"""Unit tests for orchestrator.nodes.discover."""

from __future__ import annotations

from agents.common.models import CoverageCandidate
import orchestrator.nodes.discover as discover_module
from orchestrator.nodes.discover import discover_coverage


def _candidate(cid="c1"):
    return CoverageCandidate(id=cid, kind="route", path="/x", title="X")


def test_short_circuits_on_existing_error():
    state = {"error": "boom"}
    assert discover_coverage(state) == state


def test_expansion_disabled_and_no_live_crawl_yields_empty_inventory(monkeypatch):
    monkeypatch.delenv("ENABLE_LIVE_CRAWL", raising=False)
    result = discover_coverage({})
    assert result["coverage_inventory"] == []
    assert result["metadata"]["coverage_inventory_size"] == 0


def test_expansion_enabled_but_code_dir_missing_yields_empty_inventory(monkeypatch, tmp_path):
    monkeypatch.delenv("ENABLE_LIVE_CRAWL", raising=False)
    monkeypatch.setattr(discover_module, "_repo_root", lambda: tmp_path)
    state = {"expand_coverage": True, "metadata": {"discovered_paths": ["a.py"]}}
    result = discover_coverage(state)
    assert result["coverage_inventory"] == []


def test_expansion_enabled_reads_matching_files_and_discovers(monkeypatch, tmp_path):
    monkeypatch.delenv("ENABLE_LIVE_CRAWL", raising=False)
    monkeypatch.setattr(discover_module, "_repo_root", lambda: tmp_path)
    code_dir = tmp_path / "tests" / "fixtures" / "fetched" / "code"
    code_dir.mkdir(parents=True)
    (code_dir / "src__a.py").write_text("def f(): pass")

    monkeypatch.setattr(discover_module, "discover_from_files", lambda file_map: [_candidate()] if file_map else [])

    state = {"expand_coverage": True, "metadata": {"discovered_paths": ["src/a.py"]}}
    result = discover_coverage(state)
    assert len(result["coverage_inventory"]) == 1
    assert result["metadata"]["coverage_inventory_size"] == 1


def test_expansion_enabled_skips_missing_local_files(monkeypatch, tmp_path):
    monkeypatch.delenv("ENABLE_LIVE_CRAWL", raising=False)
    monkeypatch.setattr(discover_module, "_repo_root", lambda: tmp_path)
    code_dir = tmp_path / "tests" / "fixtures" / "fetched" / "code"
    code_dir.mkdir(parents=True)  # exists, but no matching files inside

    called = []
    monkeypatch.setattr(discover_module, "discover_from_files", lambda file_map: called.append(file_map))

    state = {"expand_coverage": True, "metadata": {"discovered_paths": ["missing.py"]}}
    discover_coverage(state)
    assert called == []  # file_map ended up empty -> discover_from_files never called


def test_expansion_enabled_read_failure_is_skipped(monkeypatch, tmp_path):
    monkeypatch.delenv("ENABLE_LIVE_CRAWL", raising=False)
    monkeypatch.setattr(discover_module, "_repo_root", lambda: tmp_path)
    code_dir = tmp_path / "tests" / "fixtures" / "fetched" / "code"
    code_dir.mkdir(parents=True)
    bad_file = code_dir / "a.py"
    bad_file.write_bytes(b"\xff\xfe\x00\x01")  # invalid utf-8

    called = []
    monkeypatch.setattr(discover_module, "discover_from_files", lambda file_map: called.append(file_map))

    state = {"expand_coverage": True, "metadata": {"discovered_paths": ["a.py"]}}
    discover_coverage(state)
    assert called == []


def test_live_crawl_merges_into_inventory(monkeypatch):
    monkeypatch.setenv("ENABLE_LIVE_CRAWL", "true")
    monkeypatch.setenv("ZYVOR_BASE_URL", "https://example.com")
    monkeypatch.setattr(discover_module, "crawl_live_site", lambda url: [_candidate("crawled")])
    monkeypatch.setattr(discover_module, "merge_candidates", lambda existing, crawled: existing + crawled)

    result = discover_coverage({})
    assert len(result["coverage_inventory"]) == 1
    assert result["metadata"]["live_crawl_count"] == 1
