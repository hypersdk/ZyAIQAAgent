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

"""Unit tests for orchestrator.nodes.apply_autofix."""

from __future__ import annotations

from agents.common.models import AutofixSuggestion
import orchestrator.nodes.apply_autofix as apply_autofix_module
from orchestrator.nodes.apply_autofix import apply_autofix_node


def _suggestion():
    return AutofixSuggestion(
        test_title="t", original_selector=".old", suggested_selector=".new"
    )


def test_disabled_by_default_is_a_noop(monkeypatch):
    monkeypatch.delenv("ENABLE_AUTOFIX_APPLY", raising=False)
    state = {"autofix_suggestions": [_suggestion()]}
    assert apply_autofix_node(state) == state


def test_enabled_but_no_suggestions_is_a_noop(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTOFIX_APPLY", "true")
    state = {}
    assert apply_autofix_node(state) == state


def test_applies_patches_and_tracks_retries(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTOFIX_APPLY", "true")
    updated = [_suggestion()]
    monkeypatch.setattr(
        apply_autofix_module, "apply_autofix_patches", lambda suggestions: (updated, ["tests/a.spec.ts"])
    )

    state = {"autofix_suggestions": [_suggestion()], "metadata": {"autofix_retries": 1}}
    result = apply_autofix_node(state)

    assert result["autofix_suggestions"] == updated
    assert result["metadata"]["autofix_patches_applied"] == 1
    assert result["metadata"]["autofix_patched_files"] == ["tests/a.spec.ts"]
    assert result["metadata"]["autofix_retries"] == 2


def test_no_files_patched_does_not_bump_retries(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTOFIX_APPLY", "true")
    monkeypatch.setattr(apply_autofix_module, "apply_autofix_patches", lambda suggestions: ([], []))

    state = {"autofix_suggestions": [_suggestion()], "metadata": {}}
    result = apply_autofix_node(state)
    assert "autofix_retries" not in result["metadata"]
