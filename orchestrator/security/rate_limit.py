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

"""Per-key sliding-window rate limiter for `/api/dashboard/*` and `/api/v2/*`.

Same shape as the login lockout in `orchestrator/dashboard/auth.py`, but for
general request throughput rather than brute-force login attempts — kept
separate since the two are different concerns with different defaults.

In-process only, matching this project's current single-replica deployment
model (SQLite-backed store, one Mission Control instance). Revisit if the
service ever scales horizontally — see ROADMAP.md.
"""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque

_lock = threading.Lock()
_hits: dict[str, deque[float]] = defaultdict(deque)
_last_prune = 0.0


def _window_s() -> float:
    return float(os.environ.get("ZYVOR_API_RATE_WINDOW_S", "60"))


def _max_requests() -> int:
    return max(1, int(os.environ.get("ZYVOR_API_RATE_LIMIT", "120")))


def _prune(now: float, window: float) -> None:
    """Drop stale keys so `_hits` doesn't grow unbounded (call under `_lock`)."""
    global _last_prune
    if now - _last_prune < window:
        return
    _last_prune = now
    for key in list(_hits):
        dq = _hits[key]
        while dq and dq[0] < now - window:
            dq.popleft()
        if not dq:
            del _hits[key]


def check(key: str) -> int:
    """Record a request for `key`. Returns seconds to wait if rate-limited, else 0."""
    window = _window_s()
    limit = _max_requests()
    now = time.time()
    with _lock:
        _prune(now, window)
        dq = _hits[key]
        while dq and dq[0] < now - window:
            dq.popleft()
        if len(dq) >= limit:
            return int(dq[0] + window - now) + 1
        dq.append(now)
        return 0


def reset() -> None:
    """Clear all rate-limit state — test use only."""
    with _lock:
        _hits.clear()
        global _last_prune
        _last_prune = 0.0
