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

"""Fail-closed runtime configuration checks."""

from __future__ import annotations

import os


class SecurityConfigurationError(RuntimeError):
    pass


def validate_runtime_security() -> None:
    env = os.environ.get("ZYVOR_ENV", "development").strip().lower()
    if env not in {"production", "prod"}:
        return

    problems: list[str] = []
    required = {
        "DASHBOARD_PASSWORD": 12,
        "DASHBOARD_SECRET": 32,
        "GITHUB_WEBHOOK_SECRET": 32,
    }
    for name, minimum in required.items():
        value = os.environ.get(name, "")
        if len(value) < minimum:
            problems.append(f"{name} must contain at least {minimum} characters")
    if not os.environ.get("ZYVOR_TARGET_ALLOWLIST", "").strip():
        problems.append("ZYVOR_TARGET_ALLOWLIST is required in production")
    if os.environ.get("ZYVOR_AGENT_MODE", "read_only").lower() == "unrestricted" and os.environ.get(
        "ZYVOR_ALLOW_UNRESTRICTED_AGENT_IN_PRODUCTION", "false"
    ).lower() not in {"1", "true", "yes", "on"}:
        problems.append("unrestricted AI-agent mode is disabled in production")
    if os.environ.get("ZYVOR_ENGAGEMENT_ENFORCEMENT", "required").strip().lower() == "disabled":
        problems.append("engagement enforcement must not be disabled in production")
    if problems:
        raise SecurityConfigurationError("unsafe production configuration: " + "; ".join(problems))
