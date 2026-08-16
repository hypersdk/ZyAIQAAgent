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

"""Client-side allowlist of job kinds the MCP server will trigger.

Defense in depth on top of the server-side `jobs:write` RBAC scope (see
`orchestrator/security/rbac.py`): a leaked or overly broad service token
still shouldn't let an unvetted chat message reach the heavier/riskier job
kinds. Mirrors the pattern already used in `orchestrator/slack_gateway.py`'s
`SUPPORTED_KINDS`.

Excluded deliberately: `full` (heavy pipeline with its own PR/notify wiring —
leave to CI), `create`/`generate`/`import_codegen` (write test code),
`auth_test` (real login attempts against prod creds), `loadtest` (volumetric
— the server's SSRF allowlist doesn't defend against a chat user DoS-ing an
allowed target), and `flow`/`realtime`/`ai_flow`/`har_replay` (heavier/less
predictable — revisit once there's real usage data).
"""

from __future__ import annotations

PROBE_KINDS = frozenset(
    {
        "redirects",
        "headers",
        "cookies",
        "robots",
        "security_paths",
        "api_check",
        "sitemap_test",
        "dns_records",
        "cors",
        "transport",
    }
)

ALLOWED_KINDS = frozenset(
    {
        "smoke",
        "audit",
        "crawl_test",
        "screenshot",
        "compare",
        "ping",
        "tls",
        "vitals",
        "route_sweep",
        "api_contract",
        "regression",
        "discover",
    }
) | PROBE_KINDS
