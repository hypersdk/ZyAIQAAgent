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

"""The desktop app sets ZYVOR_DESKTOP_MODE=true when it spawns `argus
serve` (desktop/src-tauri/src/server.rs) so the dashboard hides the
Kubernetes pods/workloads panel, which is always "cluster unavailable" for
a locally-wrapped app with no cluster of its own."""

from __future__ import annotations

from fastapi.testclient import TestClient

from orchestrator.webhook import create_app


def test_workloads_panel_hidden_in_desktop_mode(monkeypatch):
    monkeypatch.setenv("ZYVOR_DESKTOP_MODE", "true")
    client = TestClient(create_app())

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="workloads"' in response.text
    assert 'style="display:none"' in response.text


def test_workloads_panel_visible_by_default(monkeypatch):
    monkeypatch.delenv("ZYVOR_DESKTOP_MODE", raising=False)
    client = TestClient(create_app())

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert 'id="workloads"' in response.text
    # The wrapping <div> around the workloads/pods section carries the
    # display:none only in desktop mode; outside it, that section's own
    # opening tag is a bare <div> (other display:none spans exist elsewhere
    # in the page unrelated to this section, e.g. the events panel).
    workloads_section = response.text.split('id="workloads"')[0].splitlines()[-1]
    assert "display:none" not in workloads_section
