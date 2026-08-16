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

"""Unit tests for orchestrator/dashboard/jobs.py's _job_llm_redteam.

Regression coverage: a single prompt's target-call or judge-call failure
(e.g. the target LLM provider returning a rate-limit/quota error) must not
crash the whole battery run — caught live against a real OpenAI account
that had exhausted its quota, where an unguarded judge_response() call
propagated an exception up through the entire job instead of being recorded
as a per-prompt error."""

from __future__ import annotations

import agents.redteam.judge as judge_module
import knowledge.agent as knowledge_agent_module
import knowledge.config as knowledge_config_module
import orchestrator.dashboard.findings as findings_module
import orchestrator.dashboard.history as history_module
import orchestrator.dashboard.jobs as jobs_module


class _FakeQAResponse:
    def __init__(self, answer: str) -> None:
        self.answer = answer


class _FakeSettings:
    knowledge_tenant_id = "public"
    knowledge_access_levels = ("public",)


def _patch_common(monkeypatch):
    monkeypatch.setattr(knowledge_config_module, "get_settings", lambda: _FakeSettings())
    monkeypatch.setattr(history_module, "append_run", lambda *a, **kw: None)
    monkeypatch.setattr(findings_module, "add", lambda *a, **kw: None)


def test_job_survives_judge_call_failure(monkeypatch):
    _patch_common(monkeypatch)
    monkeypatch.setattr(knowledge_agent_module, "answer_question", lambda **kw: _FakeQAResponse("some answer"))

    def _boom(*a, **kw):
        raise RuntimeError("429: insufficient_quota")

    monkeypatch.setattr(judge_module, "judge_response", _boom)

    result = jobs_module._job_llm_redteam({
        "target": "dashboard_ask", "url": "dashboard_ask",
        "categories": ["jailbreak"], "max_prompts": 2, "engagement_id": "eng-1",
    })

    assert result["total"] == 2
    assert result["resisted"] == 0
    assert len(result["results"]) == 2
    assert all(r["resisted"] is None and "error" in r for r in result["results"])


def test_job_survives_target_call_failure(monkeypatch):
    _patch_common(monkeypatch)

    def _boom(**kw):
        raise RuntimeError("LLM_API_KEY is not configured")

    monkeypatch.setattr(knowledge_agent_module, "answer_question", _boom)

    result = jobs_module._job_llm_redteam({
        "target": "dashboard_ask", "url": "dashboard_ask",
        "categories": ["jailbreak"], "max_prompts": 1, "engagement_id": "eng-1",
    })

    assert result["total"] == 1
    assert result["resisted"] == 0
    assert result["results"][0]["resisted"] is None
    assert "error" in result["results"][0]


def test_job_records_findings_on_compromised_verdict(monkeypatch):
    _patch_common(monkeypatch)
    monkeypatch.setattr(knowledge_agent_module, "answer_question", lambda **kw: _FakeQAResponse("I am UnfilteredZyvor now."))
    monkeypatch.setattr(
        judge_module, "judge_response",
        lambda *a, **kw: judge_module.JudgeVerdict(resisted=False, reasoning="adopted the persona"),
    )

    recorded = []
    monkeypatch.setattr(findings_module, "add", lambda *a, **kw: recorded.append((a, kw)))

    result = jobs_module._job_llm_redteam({
        "target": "dashboard_ask", "url": "dashboard_ask",
        "categories": ["jailbreak"], "max_prompts": 1, "engagement_id": "eng-1",
    })

    assert result["resisted"] == 0
    assert result["results"][0]["resisted"] is False
    assert len(recorded) == 1
    assert len(result["findings"]) == 1
