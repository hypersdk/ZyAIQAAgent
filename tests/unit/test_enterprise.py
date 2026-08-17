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

"""Unit tests for orchestrator/enterprise.py's install_enterprise: the
startup/shutdown lifecycle hooks that start/stop the durable job service
weren't exercised by any existing test (other suites build the app
without triggering FastAPI lifespan events)."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

import orchestrator.enterprise as enterprise_module


def test_install_enterprise_starts_and_stops_the_durable_service(monkeypatch):
    monkeypatch.delenv("ZYVOR_ENV", raising=False)  # avoid the production config gate
    fake_service = MagicMock()
    monkeypatch.setattr(enterprise_module, "get_service", lambda: fake_service)

    app = FastAPI()
    enterprise_module.install_enterprise(app)

    with TestClient(app):
        fake_service.start.assert_called_once()
        fake_service.stop.assert_not_called()

    fake_service.stop.assert_called_once()


def test_install_enterprise_adds_security_headers(monkeypatch):
    monkeypatch.delenv("ZYVOR_ENV", raising=False)
    monkeypatch.setattr(enterprise_module, "get_service", lambda: MagicMock())

    app = FastAPI()
    enterprise_module.install_enterprise(app)

    @app.get("/probe")
    async def probe():
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get("/probe")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "default-src 'self'" in response.headers["content-security-policy"]
