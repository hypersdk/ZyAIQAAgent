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

"""Unit tests for orchestrator.nodes.parse."""

from __future__ import annotations

from agents.common.models import ParsedRequirements, Requirement
import orchestrator.nodes.parse as parse_module
from orchestrator.nodes.parse import parse_requirements


def _req(req_id="req-1", tags=None):
    return Requirement(id=req_id, title="T", description="D", tags=tags or [])


def test_short_circuits_on_existing_error():
    state = {"error": "upstream failed", "spec_contents": ["x"]}
    assert parse_requirements(state) == state


def test_parses_and_stamps_source_and_origin(tmp_path, monkeypatch):
    monkeypatch.setattr(parse_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(parse_module, "save_requirements", lambda parsed, path: None)
    monkeypatch.setattr(
        parse_module, "parse_spec_content",
        lambda content, source: ParsedRequirements(source=source, requirements=[_req()]),
    )

    state = {
        "spec_contents": ["spec text"],
        "spec_paths": ["/tmp/spec.md"],
        "source": "document",
    }
    result = parse_requirements(state)

    assert result["requirements"][0].source_type == "document"
    assert result["requirements"][0].origin_id == "/tmp/spec.md"


def test_origin_left_unset_when_paths_and_contents_lengths_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr(parse_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(parse_module, "save_requirements", lambda parsed, path: None)
    monkeypatch.setattr(
        parse_module, "parse_spec_content",
        lambda content, source: ParsedRequirements(source=source, requirements=[_req()]),
    )

    state = {
        "spec_contents": ["a", "b"],
        "spec_paths": ["/tmp/only-one.md"],  # mismatched length vs spec_contents
        "source": "github",
    }
    result = parse_requirements(state)
    assert all(r.origin_id is None for r in result["requirements"])


def test_parse_exception_sets_error(monkeypatch):
    def raising(content, source):
        raise ValueError("bad spec")

    monkeypatch.setattr(parse_module, "parse_spec_content", raising)
    result = parse_requirements({"spec_contents": ["bad"], "spec_paths": ["/tmp/x.md"]})
    assert "Failed to parse requirements" in result["error"]


def test_coverage_gaps_merged_and_deduped_by_id(tmp_path, monkeypatch):
    monkeypatch.setattr(parse_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(parse_module, "save_requirements", lambda parsed, path: None)
    monkeypatch.setattr(
        parse_module, "parse_spec_content",
        lambda content, source: ParsedRequirements(source=source, requirements=[_req("req-existing")]),
    )
    monkeypatch.setattr(
        parse_module, "gaps_to_requirements",
        lambda gaps: [_req("req-existing", tags=["coverage"]), _req("req-new", tags=["coverage"])],
    )

    state = {"spec_contents": ["x"], "spec_paths": ["/tmp/x.md"], "coverage_gaps": ["gap1"]}
    result = parse_requirements(state)

    ids = [r.id for r in result["requirements"]]
    assert ids == ["req-existing", "req-new"]  # duplicate id from gaps not re-added
    assert result["metadata"]["coverage_requirements_added"] == 1  # only req-new has the coverage tag among gap-sourced


def test_coverage_max_new_tests_env_var_limits_gap_requirements(tmp_path, monkeypatch):
    monkeypatch.setattr(parse_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(parse_module, "save_requirements", lambda parsed, path: None)
    monkeypatch.setattr(
        parse_module, "parse_spec_content",
        lambda content, source: ParsedRequirements(source=source, requirements=[]),
    )
    monkeypatch.setenv("COVERAGE_MAX_NEW_TESTS", "1")

    received_gaps = []

    def fake_gaps_to_requirements(gaps):
        received_gaps.append(gaps)
        return [_req(f"req-{i}", tags=["coverage"]) for i in range(len(gaps))]

    monkeypatch.setattr(parse_module, "gaps_to_requirements", fake_gaps_to_requirements)

    state = {"spec_contents": [], "spec_paths": [], "coverage_gaps": ["g1", "g2", "g3"]}
    parse_requirements(state)
    assert received_gaps == [["g1"]]  # sliced to COVERAGE_MAX_NEW_TESTS before being passed in


def test_no_requirements_from_specs_is_an_error():
    result = parse_requirements({"spec_contents": [], "spec_paths": []})
    # empty spec_contents with nothing else -> falls into the "nothing at all" branch below
    assert "No requirements extracted" in result["error"]


def test_no_requirements_and_no_specs_and_no_gaps_is_an_error(monkeypatch):
    monkeypatch.setattr(
        parse_module, "parse_spec_content",
        lambda content, source: ParsedRequirements(source=source, requirements=[]),
    )
    result = parse_requirements({"spec_contents": ["x"], "spec_paths": ["/tmp/x.md"]})
    assert "No requirements extracted" in result["error"]


def test_successful_parse_persists_and_returns_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(parse_module, "_repo_root", lambda: tmp_path)
    saved = {}
    monkeypatch.setattr(
        parse_module, "save_requirements",
        lambda parsed, path: saved.update(parsed=parsed, path=path),
    )
    monkeypatch.setattr(
        parse_module, "parse_spec_content",
        lambda content, source: ParsedRequirements(
            source=source, requirements=[_req("req-1", tags=["coverage"]), _req("req-2")]
        ),
    )

    state = {"spec_contents": ["x"], "spec_paths": ["/tmp/x.md"], "source": "github", "metadata": {"k": "v"}}
    result = parse_requirements(state)

    assert len(result["requirements"]) == 2
    assert result["metadata"]["coverage_requirements_added"] == 1
    assert result["metadata"]["k"] == "v"  # existing metadata preserved
    assert saved["path"] == tmp_path / "tests" / "fixtures" / "requirements.json"
