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

"""Attack-graph (Mermaid flowchart) generation from a run's findings, grouped
by category -> severity -> count.

Pure Python, no new dependency — this only emits the Mermaid graph
*definition* text; rendering happens client-side via the vendored
`templates/vendor/mermaid.min.js` (see that directory's README for why it's
vendored rather than loaded from a CDN).
"""

from __future__ import annotations

import re
from typing import Any

_SEVERITY_ORDER = ("critical", "high", "medium", "low", "info")

_SEVERITY_CLASS_DEFS = (
    "    classDef critical fill:#dc2626,color:#fff",
    "    classDef high fill:#ea580c,color:#fff",
    "    classDef medium fill:#ca8a04,color:#fff",
    "    classDef low fill:#65a30d,color:#fff",
    "    classDef info fill:#64748b,color:#fff",
)


def _node_id(prefix: str, raw: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", raw.strip().lower()).strip("_") or "unknown"
    return f"{prefix}_{slug}"


def _escape_label(text: str) -> str:
    return text.replace('"', "'")


def build_mermaid_graph(findings: list[dict[str, Any]]) -> str:
    """Return a Mermaid `graph TD` definition, or "" if there's nothing to draw."""
    if not findings:
        return ""

    counts: dict[tuple[str, str], int] = {}
    for item in findings:
        category = str(item.get("category") or "uncategorized")
        severity = str(item.get("severity") or "medium")
        if severity not in _SEVERITY_ORDER:
            severity = "medium"
        counts[(category, severity)] = counts.get((category, severity), 0) + 1

    lines = ["graph TD"]
    for category in sorted({c for c, _ in counts}):
        cat_node = _node_id("cat", category)
        lines.append(f'    {cat_node}["{_escape_label(category)}"]')
        for severity in _SEVERITY_ORDER:
            n = counts.get((category, severity))
            if not n:
                continue
            sev_node = _node_id("sev", f"{category}_{severity}")
            lines.append(f'    {sev_node}["{severity} ({n})"]:::{severity}')
            lines.append(f"    {cat_node} --> {sev_node}")
    lines.extend(_SEVERITY_CLASS_DEFS)
    return "\n".join(lines)
