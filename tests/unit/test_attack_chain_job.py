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

"""Unit tests for orchestrator/dashboard/jobs.py's _job_attack_chain."""

from __future__ import annotations

import pytest

import agents.exploit.poc_generator as poc_generator_module
import orchestrator.dashboard.findings as findings_module
import orchestrator.dashboard.history as history_module
import orchestrator.dashboard.jobs as jobs_module
import orchestrator.persistence.store as store_module
import orchestrator.security.sandbox as sandbox_module


class _FakeStore:
    def audit(self, *a, **kw):
        pass


def _patch_common(monkeypatch, tmp_path):
    monkeypatch.setattr(history_module, "append_run", lambda *a, **kw: None)
    monkeypatch.setattr(store_module, "get_store", lambda: _FakeStore())
    monkeypatch.setattr(jobs_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(sandbox_module, "available", lambda: True)


def _base_params(**overrides):
    params = {
        "url": "https://x.io", "objective": "escalate SQLi to RCE",
        "max_steps": 5, "timeout_s": 30,
    }
    params.update(overrides)
    return params


def test_raises_when_sandbox_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(history_module, "append_run", lambda *a, **kw: None)
    monkeypatch.setattr(store_module, "get_store", lambda: _FakeStore())
    monkeypatch.setattr(jobs_module, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(sandbox_module, "available", lambda: False)

    with pytest.raises(RuntimeError, match="sandbox unavailable"):
        jobs_module._job_attack_chain(_base_params())


def test_stops_immediately_when_planner_signals_stop(monkeypatch, tmp_path):
    _patch_common(monkeypatch, tmp_path)
    monkeypatch.setattr(
        poc_generator_module, "plan_next_chain_step",
        lambda objective, url, prior, **kw: poc_generator_module.ChainStepPlan(description=None),
    )
    generate_calls = []
    monkeypatch.setattr(
        poc_generator_module, "generate_verification_poc",
        lambda *a, **kw: generate_calls.append(1),
    )
    monkeypatch.setattr(findings_module, "add", lambda *a, **kw: None)

    result = jobs_module._job_attack_chain(_base_params())

    assert result["steps"] == []
    assert result["confirmed_count"] == 0
    assert result["stop_reason"] == "planner signalled stop"
    assert generate_calls == []  # never asked to generate a PoC for zero planned steps


def test_stops_after_first_unverified_step(monkeypatch, tmp_path):
    _patch_common(monkeypatch, tmp_path)
    plan_calls = []

    def fake_plan(objective, url, prior, **kw):
        plan_calls.append(list(prior))
        return poc_generator_module.ChainStepPlan(description=f"step {len(prior) + 1}")

    monkeypatch.setattr(poc_generator_module, "plan_next_chain_step", fake_plan)
    monkeypatch.setattr(
        poc_generator_module, "generate_verification_poc",
        lambda description, url, **kw: poc_generator_module.GeneratedPoC(code="print('x')", finding_description=description),
    )
    monkeypatch.setattr(
        sandbox_module, "run_python",
        lambda code, **kw: sandbox_module.SandboxResult(
            exit_code=0, stdout="VERIFIED: false - nope\n", timed_out=False, network_policy_applied=False,
        ),
    )
    monkeypatch.setattr(findings_module, "add", lambda *a, **kw: None)

    result = jobs_module._job_attack_chain(_base_params())

    assert len(result["steps"]) == 1  # stopped after the first (unverified) step
    assert result["confirmed_count"] == 0
    assert result["stop_reason"] == "step 1 did not verify"
    assert len(plan_calls) == 1


def test_multi_step_chain_confirms_and_raises_chain_finding(monkeypatch, tmp_path):
    _patch_common(monkeypatch, tmp_path)

    def fake_plan(objective, url, prior, **kw):
        if len(prior) >= 2:
            return poc_generator_module.ChainStepPlan(description=None)
        return poc_generator_module.ChainStepPlan(description=f"step {len(prior) + 1}")

    monkeypatch.setattr(poc_generator_module, "plan_next_chain_step", fake_plan)
    monkeypatch.setattr(
        poc_generator_module, "generate_verification_poc",
        lambda description, url, **kw: poc_generator_module.GeneratedPoC(code="print('x')", finding_description=description),
    )
    monkeypatch.setattr(
        sandbox_module, "run_python",
        lambda code, **kw: sandbox_module.SandboxResult(
            exit_code=0, stdout="VERIFIED: true - confirmed\n", timed_out=False, network_policy_applied=False,
        ),
    )
    recorded = []
    monkeypatch.setattr(findings_module, "add", lambda *a, **kw: recorded.append(a))

    result = jobs_module._job_attack_chain(_base_params())

    assert result["confirmed_count"] == 2
    assert result["stop_reason"] == "planner signalled stop"
    # one finding per confirmed step (2) + one chain-level "critical" finding
    assert len(recorded) == 3
    severities = [call[1] for call in recorded]
    assert severities.count("critical") == 1
    assert severities.count("high") == 2
    assert any(f["category"] == "confirmed-attack-chain" for f in result["findings"])


def test_respects_max_steps_cap(monkeypatch, tmp_path):
    _patch_common(monkeypatch, tmp_path)
    monkeypatch.setattr(
        poc_generator_module, "plan_next_chain_step",
        lambda objective, url, prior, **kw: poc_generator_module.ChainStepPlan(description=f"step {len(prior) + 1}"),
    )
    monkeypatch.setattr(
        poc_generator_module, "generate_verification_poc",
        lambda description, url, **kw: poc_generator_module.GeneratedPoC(code="print('x')", finding_description=description),
    )
    monkeypatch.setattr(
        sandbox_module, "run_python",
        lambda code, **kw: sandbox_module.SandboxResult(
            exit_code=0, stdout="VERIFIED: true - confirmed\n", timed_out=False, network_policy_applied=False,
        ),
    )
    monkeypatch.setattr(findings_module, "add", lambda *a, **kw: None)

    result = jobs_module._job_attack_chain(_base_params(max_steps=2))

    assert len(result["steps"]) == 2
    assert result["stop_reason"] == "max_steps reached"
