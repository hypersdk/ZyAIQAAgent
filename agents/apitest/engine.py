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

"""Run the Node API-contract runner and parse its JSON output."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable, Optional


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def run_api_contract(
    base: str,
    *,
    spec: Any = None,
    mode: str = "spec",
    workflow: Optional[list[dict[str, Any]]] = None,
    auth: Optional[dict[str, Any]] = None,
    include_writes: bool = False,
    insecure: bool = False,
    path_params: Optional[dict[str, str]] = None,
    selected_paths: Optional[list[str]] = None,
    max_endpoints: int = 60,
    out_dir: Optional[Path] = None,
    on_line: Optional[Callable[[str], None]] = None,
) -> dict[str, Any]:
    """Drive api-contract.mjs; stream progress; return result JSON."""
    repo_root = _repo_root()
    script = repo_root / "playwright" / "scripts" / "api-contract.mjs"
    if not script.exists():
        raise RuntimeError("api-contract.mjs not found")

    cfg: dict[str, Any] = {
        "base": base,
        "mode": mode,
        "insecure": insecure,
        "include_writes": include_writes,
        "max_endpoints": max_endpoints,
    }
    if spec is not None:
        cfg["spec"] = spec
    if workflow is not None:
        cfg["workflow"] = workflow
    if auth:
        cfg["auth"] = auth
    if path_params:
        cfg["path_params"] = path_params
    if selected_paths:
        cfg["selected_paths"] = selected_paths

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(cfg, fh)
        cfg_file = fh.name

    env = {**os.environ}
    if insecure:
        env["ZYVOR_IGNORE_HTTPS_ERRORS"] = "true"

    proc = subprocess.Popen(
        ["node", str(script), cfg_file, str(out_dir or "")],
        cwd=repo_root, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
    )

    def _drain() -> None:
        assert proc.stderr is not None
        for line in proc.stderr:
            if on_line and line.strip():
                try:
                    on_line(line.rstrip("\n"))
                except Exception:
                    pass

    t = threading.Thread(target=_drain, daemon=True)
    t.start()
    stdout, _ = proc.communicate()
    t.join(timeout=2)
    try:
        os.unlink(cfg_file)
    except OSError:
        pass

    if proc.returncode != 0 or not stdout.strip():
        raise RuntimeError(f"api contract run failed (exit {proc.returncode})")
    return json.loads(stdout)
