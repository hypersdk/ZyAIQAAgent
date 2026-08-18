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

"""Run the Node flow runner and parse its JSON output."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def run_flow(
    url: str,
    steps: list[dict[str, Any]],
    out_dir: Path,
    *,
    insecure: bool = False,
    record: bool = True,
    trace: bool = True,
    username: str = "",
    password: str = "",
    session: str = "",
    stop_on_fail: bool = False,
    on_line: Optional[Callable[[str], None]] = None,
) -> dict[str, Any]:
    """Drive the journey via flow-run.mjs; stream progress; return result JSON."""
    repo_root = _repo_root()
    script = repo_root / "playwright" / "scripts" / "flow-run.mjs"
    if not script.exists():
        raise RuntimeError("flow-run.mjs not found")

    flow = {"base": url, "steps": steps, "record": record, "trace": trace, "stop_on_fail": stop_on_fail}
    if session:
        flow["session"] = session
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(flow, fh)
        flow_file = fh.name

    env = {**os.environ, "ZYVOR_BASE_URL": url}
    if insecure:
        env["ZYVOR_IGNORE_HTTPS_ERRORS"] = "true"
    if username:
        env["ZYVOR_TEST_USER"] = username
    if password:
        env["ZYVOR_TEST_PASSWORD"] = password

    proc = subprocess.Popen(
        ["node", str(script), flow_file, str(out_dir)],
        cwd=repo_root, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
    )

    import threading

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
        os.unlink(flow_file)
    except OSError:
        pass

    if proc.returncode != 0 or not stdout.strip():
        raise RuntimeError(f"flow run failed (exit {proc.returncode})")
    return json.loads(stdout)
