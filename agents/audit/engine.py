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

"""Run the Node site-audit script and parse its JSON output."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable, Optional

VALID_CHECKS = ["a11y", "links", "seo", "console", "perf", "headers", "responsive"]


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def run_audit(
    url: str,
    checks: list[str],
    *,
    max_pages: int = 20,
    insecure: bool = False,
    username: str = "",
    password: str = "",
    on_line: Optional[Callable[[str], None]] = None,
) -> dict[str, Any]:
    """Crawl `url` and run per-page QA checks. Returns the parsed audit JSON."""
    repo_root = _repo_root()
    script = repo_root / "playwright" / "scripts" / "audit-site.mjs"
    if not script.exists():
        raise RuntimeError("audit-site.mjs not found")

    selected = [c for c in checks if c in VALID_CHECKS] or ["a11y", "links", "seo", "console", "perf", "headers"]

    env = {**os.environ}
    env["ZYVOR_BASE_URL"] = url
    if insecure:
        env["ZYVOR_IGNORE_HTTPS_ERRORS"] = "true"
    if username:
        env["ZYVOR_TEST_USER"] = username
    if password:
        env["ZYVOR_TEST_PASSWORD"] = password
    env["ZYVOR_AUDIT_REPORTS_DIR"] = str(repo_root / "reports")

    cmd = ["node", str(script), url, str(max_pages), ",".join(selected)]
    proc = subprocess.Popen(
        cmd, cwd=repo_root, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
    )

    import threading

    def _drain_stderr() -> None:
        assert proc.stderr is not None
        for line in proc.stderr:
            if on_line and line.strip():
                try:
                    on_line(line.rstrip("\n"))
                except Exception:
                    pass

    t = threading.Thread(target=_drain_stderr, daemon=True)
    t.start()

    stdout, _ = proc.communicate()
    t.join(timeout=2)

    if proc.returncode != 0 or not stdout.strip():
        raise RuntimeError(f"audit failed (exit {proc.returncode})")
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"audit produced invalid JSON: {exc}")
