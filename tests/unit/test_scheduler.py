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

"""Unit tests for orchestrator/dashboard/scheduler.py -- a thin,
backward-compatible wrapper over the durable store/service. Previously
had zero coverage (0%)."""

from __future__ import annotations

from unittest.mock import MagicMock

import orchestrator.dashboard.scheduler as scheduler


def test_add_persists_schedule_and_starts_the_service(monkeypatch):
    fake_store = MagicMock()
    fake_store.add_schedule.return_value = {"id": "sched-1", "kind": "smoke"}
    fake_service = MagicMock()

    monkeypatch.setattr(scheduler, "get_store", lambda: fake_store)
    monkeypatch.setattr(scheduler, "get_service", lambda: fake_service)

    result = scheduler.add("smoke", {"url": "https://example.org"}, 300)

    assert result == {"id": "sched-1", "kind": "smoke"}
    fake_store.add_schedule.assert_called_once_with(
        "smoke", {"url": "https://example.org"}, 300, requested_by="legacy-dashboard"
    )
    fake_service.start.assert_called_once()


def test_remove_delegates_to_store(monkeypatch):
    fake_store = MagicMock()
    fake_store.remove_schedule.return_value = True
    monkeypatch.setattr(scheduler, "get_store", lambda: fake_store)

    assert scheduler.remove("sched-1") is True
    fake_store.remove_schedule.assert_called_once_with("sched-1")


def test_listing_delegates_to_store(monkeypatch):
    fake_store = MagicMock()
    fake_store.list_schedules.return_value = [{"id": "sched-1"}]
    monkeypatch.setattr(scheduler, "get_store", lambda: fake_store)

    assert scheduler.listing() == [{"id": "sched-1"}]


def test_ensure_thread_starts_the_service(monkeypatch):
    fake_service = MagicMock()
    monkeypatch.setattr(scheduler, "get_service", lambda: fake_service)

    scheduler._ensure_thread()

    fake_service.start.assert_called_once()
