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

"""Remediation agent gate tests (no LLM required)."""

from __future__ import annotations

import pytest

from knowledge.config import clear_settings_cache
from knowledge.remediation import clear_remediation_agent_cache, plan_remediation


def test_remediation_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENABLE_REMEDIATION_AGENT", "false")
    clear_settings_cache()
    clear_remediation_agent_cache()
    result = plan_remediation(issue="restart hubble-relay")
    assert result["enabled"] is False
    assert "ENABLE_REMEDIATION_AGENT" in (result.get("blocked_reason") or "")
    clear_settings_cache()
    clear_remediation_agent_cache()
