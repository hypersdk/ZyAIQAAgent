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

"""Unit tests for orchestrator.nodes.generate."""

from __future__ import annotations

from agents.common.models import Requirement
import orchestrator.nodes.generate as generate_module
from orchestrator.nodes.generate import generate_tests


def _req(req_id="req-1", tags=None):
    return Requirement(id=req_id, title="T", description="D", tags=tags or [])


class _FakeStore:
    def __init__(self, raise_on_link=False):
        self.links = []
        self.raise_on_link = raise_on_link

    def link_requirement_test(self, req_id, path):
        if self.raise_on_link:
            raise RuntimeError("store unavailable")
        self.links.append((req_id, path))


def test_no_requirements_returns_empty(monkeypatch):
    result = generate_tests({"requirements": []})
    assert result["generated_tests"] == []


def test_generates_story_requirements(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(generate_module, "collect_existing_hashes", lambda output_dir: {})
    store = _FakeStore()
    monkeypatch.setattr(generate_module, "get_store", lambda: store)

    test_file = tmp_path / "tests" / "generated" / "req-1.spec.ts"

    def fake_generate(req, output_dir, *, coverage_mode, existing_hashes):
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("// generated")
        return str(test_file), True, []

    monkeypatch.setattr(generate_module, "generate_and_validate_test", fake_generate)

    result = generate_tests({"requirements": [_req()]})

    assert result["generated_tests"] == [str(test_file)]
    assert result["metadata"]["quality_passed"] == 1
    assert result["metadata"]["quality_regenerated"] == 0
    assert store.links == [("req-1", str(test_file))]


def test_quality_regenerated_stats_accumulate(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(generate_module, "collect_existing_hashes", lambda output_dir: {})
    monkeypatch.setattr(generate_module, "get_store", lambda: _FakeStore())

    test_file = tmp_path / "tests" / "generated" / "req-1.spec.ts"

    def fake_generate(req, output_dir, *, coverage_mode, existing_hashes):
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("// generated")
        return str(test_file), False, ["issue-a", "issue-b"]

    monkeypatch.setattr(generate_module, "generate_and_validate_test", fake_generate)

    result = generate_tests({"requirements": [_req()]})

    assert result["metadata"]["quality_passed"] == 0
    assert result["metadata"]["quality_regenerated"] == 1
    assert result["metadata"]["quality_issues"] == 2


def test_link_requirement_test_failure_does_not_block_generation(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(generate_module, "collect_existing_hashes", lambda output_dir: {})
    monkeypatch.setattr(generate_module, "get_store", lambda: _FakeStore(raise_on_link=True))

    test_file = tmp_path / "tests" / "generated" / "req-1.spec.ts"

    def fake_generate(req, output_dir, *, coverage_mode, existing_hashes):
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("// generated")
        return str(test_file), True, []

    monkeypatch.setattr(generate_module, "generate_and_validate_test", fake_generate)

    result = generate_tests({"requirements": [_req()]})
    assert result["generated_tests"] == [str(test_file)]


def test_generation_exception_falls_back_to_template(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(generate_module, "collect_existing_hashes", lambda output_dir: {})
    monkeypatch.setattr(generate_module, "get_store", lambda: _FakeStore())

    def raising_generate(req, output_dir, *, coverage_mode, existing_hashes):
        raise RuntimeError("LLM unavailable")

    fallback_path = tmp_path / "fallback.spec.ts"
    monkeypatch.setattr(generate_module, "generate_and_validate_test", raising_generate)
    monkeypatch.setattr(generate_module, "render_template_fallback", lambda req, output_dir, **kw: str(fallback_path))

    result = generate_tests({"requirements": [_req()]})
    assert result["generated_tests"] == [str(fallback_path)]


def test_coverage_requirements_use_coverage_mode_and_are_capped(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(generate_module, "collect_existing_hashes", lambda output_dir: {})
    monkeypatch.setattr(generate_module, "get_store", lambda: _FakeStore())
    monkeypatch.setenv("COVERAGE_MAX_NEW_TESTS", "2")

    seen_modes = []

    def fake_generate(req, output_dir, *, coverage_mode, existing_hashes):
        seen_modes.append(coverage_mode)
        path = tmp_path / f"coverage-{req.id}.spec.ts"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// generated")
        return str(path), True, []

    monkeypatch.setattr(generate_module, "generate_and_validate_test", fake_generate)

    reqs = [_req(req_id=f"req-{i}", tags=["coverage"]) for i in range(5)]
    result = generate_tests({"requirements": reqs})

    assert len(result["generated_tests"]) == 2  # capped by COVERAGE_MAX_NEW_TESTS
    assert all(mode is True for mode in seen_modes)
    assert result["metadata"]["coverage_tests_generated"] == 2


def test_coverage_generation_exception_falls_back_with_prefix(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(generate_module, "collect_existing_hashes", lambda output_dir: {})
    monkeypatch.setattr(generate_module, "get_store", lambda: _FakeStore())

    def raising_generate(req, output_dir, *, coverage_mode, existing_hashes):
        raise RuntimeError("boom")

    fallback_calls = []

    def fake_fallback(req, output_dir, **kwargs):
        fallback_calls.append(kwargs.get("filename_prefix"))
        return str(tmp_path / f"{kwargs.get('filename_prefix', '')}{req.id}.spec.ts")

    monkeypatch.setattr(generate_module, "generate_and_validate_test", raising_generate)
    monkeypatch.setattr(generate_module, "render_template_fallback", fake_fallback)

    result = generate_tests({"requirements": [_req(tags=["coverage"])]})
    assert fallback_calls == ["coverage-"]
    assert len(result["generated_tests"]) == 1
