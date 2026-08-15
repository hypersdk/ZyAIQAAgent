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

from __future__ import annotations

import pytest

from orchestrator.security import rate_limit


@pytest.fixture(autouse=True)
def _clean_rate_limit_state():
    rate_limit.reset()
    yield
    rate_limit.reset()


def test_allows_requests_under_the_limit(monkeypatch):
    monkeypatch.setenv("ZYVOR_API_RATE_LIMIT", "3")
    monkeypatch.setenv("ZYVOR_API_RATE_WINDOW_S", "60")

    for _ in range(3):
        assert rate_limit.check("1.2.3.4") == 0


def test_blocks_once_the_limit_is_exceeded(monkeypatch):
    monkeypatch.setenv("ZYVOR_API_RATE_LIMIT", "2")
    monkeypatch.setenv("ZYVOR_API_RATE_WINDOW_S", "60")

    assert rate_limit.check("1.2.3.4") == 0
    assert rate_limit.check("1.2.3.4") == 0
    wait = rate_limit.check("1.2.3.4")
    assert wait > 0


def test_keys_are_independent(monkeypatch):
    monkeypatch.setenv("ZYVOR_API_RATE_LIMIT", "1")
    monkeypatch.setenv("ZYVOR_API_RATE_WINDOW_S", "60")

    assert rate_limit.check("1.2.3.4") == 0
    assert rate_limit.check("1.2.3.4") > 0
    # A different key has its own budget.
    assert rate_limit.check("5.6.7.8") == 0


def test_window_expiry_allows_requests_again(monkeypatch):
    monkeypatch.setenv("ZYVOR_API_RATE_LIMIT", "1")
    monkeypatch.setenv("ZYVOR_API_RATE_WINDOW_S", "60")

    times = iter([1000.0, 1000.0, 1061.0])
    monkeypatch.setattr(rate_limit.time, "time", lambda: next(times))

    assert rate_limit.check("1.2.3.4") == 0
    assert rate_limit.check("1.2.3.4") > 0
    assert rate_limit.check("1.2.3.4") == 0
