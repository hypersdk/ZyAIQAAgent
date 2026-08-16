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

"""Authorization gate for elevated-risk security-testing job kinds.

`TargetPolicy` (`orchestrator/security/target_policy.py`) prevents SSRF — it says
nothing about whether the operator is actually authorized to test a given target.
This module is that missing attestation: an admin-issued `engagements` record
(`orchestrator.persistence.store.MissionControlStore`) that a job must explicitly
cite before `_validate()` in `orchestrator/dashboard/jobs.py` lets it proceed.
Mirrors `orchestrator.security.agent_policy.AgentPolicy`'s mode/env-var/fail-closed
shape rather than inventing a new one.
"""

from __future__ import annotations

import fnmatch
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from urllib.parse import urlsplit

EngagementTier = Literal["active_recon", "exploit"]

TIER_RANK: dict[str, int] = {"active_recon": 1, "exploit": 2}


def _epoch(iso_timestamp: str) -> float:
    return datetime.fromisoformat(iso_timestamp).timestamp()


@dataclass(frozen=True)
class EngagementPolicy:
    enforcement: Literal["disabled", "required"] = "required"

    @classmethod
    def from_env(cls) -> "EngagementPolicy":
        raw = os.environ.get("ZYVOR_ENGAGEMENT_ENFORCEMENT", "required").strip().lower()
        enforcement = raw if raw in {"disabled", "required"} else "required"
        return cls(enforcement=enforcement)  # type: ignore[arg-type]

    def require(
        self,
        *,
        target_url: str,
        min_tier: EngagementTier,
        engagement_id: str | None,
        actor: str = "",
    ) -> None:
        """Raise ValueError (→ HTTP 400 via `_validate()`) unless `engagement_id`
        names a live, sufficiently-scoped engagement covering `target_url`."""
        if self.enforcement == "disabled":
            return

        from orchestrator.persistence.store import get_store

        store = get_store()
        if not engagement_id:
            raise ValueError(
                "this job requires an authorized security engagement — "
                "create one via POST /api/v2/engagements and pass its id as engagement_id"
            )
        engagement = store.get_engagement(engagement_id)
        if engagement is None:
            raise ValueError(f"unknown engagement_id {engagement_id!r}")
        if engagement.get("revoked_at"):
            raise ValueError("engagement has been revoked")
        expires_at = engagement.get("expires_at")
        if expires_at and _epoch(expires_at) < time.time():
            raise ValueError("engagement has expired")

        tier = str(engagement.get("tier", ""))
        if TIER_RANK.get(tier, 0) < TIER_RANK.get(min_tier, 0):
            raise ValueError(
                f"engagement tier {tier!r} is insufficient for this job (requires {min_tier!r})"
            )

        host = (urlsplit(target_url).hostname or target_url or "").lower()
        pattern = str(engagement.get("target_pattern", "")).lower()
        if not host or not fnmatch.fnmatchcase(host, pattern):
            raise ValueError(f"target {host!r} is outside engagement scope {pattern!r}")

        store.audit(
            "engagement.use",
            actor=actor,
            resource_type="engagement",
            resource_id=engagement_id,
            detail={"target": host, "min_tier": min_tier},
        )
