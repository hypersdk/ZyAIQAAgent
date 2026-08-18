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

"""Agentic AI-flow — the decider half. Spawns ai-flow.mjs, and for each page
observation asks the LLM (or an injected decider) for the next action, until the
agent reports `done` or the browser hits its step cap.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import threading
from pathlib import Path
from typing import Any, Callable, Optional

OBS = "@@OBS@@"
RESULT = "@@RESULT@@"

Decider = Callable[[str, dict[str, Any], list[str]], dict[str, Any]]


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def llm_decider(goal: str, obs: dict[str, Any], history: list[str]) -> dict[str, Any]:
    """Ask the configured LLM for the next action given the page observation."""
    from agents.common.llm import get_llm, load_prompt
    from langchain_core.messages import HumanMessage, SystemMessage

    payload = {"goal": goal, "step": obs.get("step"), "url": obs.get("url"),
               "title": obs.get("title"), "elements": obs.get("elements", []),
               "texts": obs.get("texts", []), "history": history[-10:]}
    resp = get_llm().invoke([
        SystemMessage(content=load_prompt("ai_flow")),
        HumanMessage(content=json.dumps(payload)),
    ])
    raw = (resp.content if isinstance(resp.content, str) else str(resp.content)).strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        raw = m.group(1).strip()
    # take the first {...} object
    b = raw.find("{")
    e = raw.rfind("}")
    if b >= 0 and e > b:
        raw = raw[b:e + 1]
    return json.loads(raw)


def _goal_specs(goal: str) -> dict[str, Any]:
    g = goal.lower()
    cpu = None
    m = re.search(r"(\d+)\s*(?:v?cpu|core|vcpus|cpus)", g)
    if m:
        cpu = m.group(1)
    mem = None
    m = re.search(r"(\d+)\s*(?:gb|gi|g)\b", g)
    if m:
        mem = m.group(1)
    # OS/template keyword
    os_kw = next((w for w in ("ubuntu", "fedora", "debian", "centos", "rocky", "windows", "alpine", "cirros")
                  if w in g), None)
    return {"cpu": cpu, "mem": mem, "os": os_kw}


def heuristic_decider(goal: str, obs: dict[str, Any], history: list[str]) -> dict[str, Any]:
    """LLM-free rule-based agent: opens a create wizard, fills name/OS/CPU/RAM,
    advances through Next steps, and submits. Handles the common VM-wizard shape."""
    spec = _goal_specs(goal)
    els = obs.get("elements", [])
    hist = " ".join(history).lower()

    def find(pred):
        return next((e for e in els if pred(e)), None)

    def nm(e):
        return (e.get("name") or "").lower()

    def is_text_input(e):
        r = e.get("role", "")
        return r == "textarea" or (r.startswith("input:") and r.split(":", 1)[1] in
                                   ("text", "number", "email", "password", "search", "tel", "url", ""))

    step = obs.get("step", 1)
    # 0. If the goal's target already shows up, we're likely done
    joined = " ".join(obs.get("texts", [])).lower()
    if step > 3 and spec["os"] and ("running" in joined or "created" in joined or "succeeded" in joined):
        return {"action": "done", "success": True, "summary": f"{spec['os']} resource appears created"}

    # 1. Open a create/new wizard if we haven't yet
    if "click" not in hist or all("create" not in h and "new" not in h for h in history):
        b = find(lambda e: e.get("enabled") and re.search(r"\b(create|new|add|\+)\b", nm(e)) and "vm" in nm(e) + goal.lower())
        b = b or find(lambda e: e.get("enabled") and re.search(r"\bcreate\b|\bnew\b|\badd\b", nm(e)))
        if b and f"click {b['i']}" not in hist:
            return {"action": "click", "i": b["i"], "reason": f"open wizard via '{b.get('name')}'"}

    # 2. Fill a name field if empty
    name_field = find(lambda e: is_text_input(e) and not e.get("value")
                      and re.search(r"name|my-vm", nm(e)))
    if name_field and f"fill {name_field['i']}" not in hist:
        return {"action": "fill", "i": name_field["i"], "value": f"qa-{spec['os'] or 'vm'}-01", "reason": "set the name"}

    # 3. Pick the OS/template option
    if spec["os"]:
        opt = find(lambda e: e.get("enabled") and spec["os"] in nm(e))
        if opt and f"click {opt['i']}" not in hist:
            return {"action": "click", "i": opt["i"], "reason": f"choose {spec['os']} template"}

    # 4. Fill CPU / memory fields
    if spec["cpu"]:
        f = find(lambda e: is_text_input(e) and re.search(r"cpu|core|vcpu", nm(e)))
        if f and f.get("value") != spec["cpu"] and f"fill {f['i']} = {spec['cpu']}" not in hist:
            return {"action": "fill", "i": f["i"], "value": spec["cpu"], "reason": f"set CPU={spec['cpu']}"}
    if spec["mem"]:
        f = find(lambda e: is_text_input(e) and re.search(r"mem|ram", nm(e)))
        if f and f"fill {f['i']} = {spec['mem']}" not in hist:
            return {"action": "fill", "i": f["i"], "value": spec["mem"], "reason": f"set memory={spec['mem']}"}

    # 5. Advance the wizard
    nxt = find(lambda e: e.get("enabled") and re.fullmatch(r"next\s*.*", nm(e)))
    if nxt:
        return {"action": "click", "i": nxt["i"], "reason": "advance to the next step"}

    # 6. Submit (Create / Finish / Deploy) when there's no Next
    submit = find(lambda e: e.get("enabled") and re.search(r"\b(create vm|create|finish|deploy|submit|confirm)\b", nm(e)))
    if submit and f"click {submit['i']}" not in hist:
        return {"action": "click", "i": submit["i"], "reason": f"submit via '{submit.get('name')}'"}

    # 7. Nothing left to do
    return {"action": "done", "success": step > 2,
            "summary": "heuristic agent finished (no further wizard action found)"}


def run_ai_flow(
    url: str,
    goal: str,
    out_dir: Path,
    *,
    insecure: bool = False,
    session: str = "",
    max_steps: int = 20,
    decider: Optional[Decider] = None,
    on_line: Optional[Callable[[str], None]] = None,
) -> dict[str, Any]:
    """Drive the browser toward `goal`; return the transcript + video + trace."""
    repo_root = _repo_root()
    script = repo_root / "playwright" / "scripts" / "ai-flow.mjs"
    if not script.exists():
        raise RuntimeError("ai-flow.mjs not found")
    if decider is not None:
        decide, mode = decider, "custom"
    else:
        from agents.parser.agent import _llm_available

        if _llm_available():
            _warned = {"done": False}

            def decide(goal_, obs_, hist_):  # LLM with a per-step heuristic fallback
                try:
                    return llm_decider(goal_, obs_, hist_)
                except Exception as exc:
                    if on_line and not _warned["done"]:
                        on_line(f"ai: LLM unavailable ({str(exc)[:80]}) — falling back to the heuristic agent")
                        _warned["done"] = True
                    return heuristic_decider(goal_, obs_, hist_)
            mode = "llm"
        else:
            decide, mode = heuristic_decider, "heuristic"
    if on_line:
        on_line(f"ai: deciding with the {mode} agent")

    cfg = {"url": url, "goal": goal, "insecure": insecure, "max_steps": max_steps}
    if session:
        cfg["session"] = session
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(cfg, fh)
        cfg_file = fh.name

    env = {**os.environ}
    if insecure:
        env["ZYVOR_IGNORE_HTTPS_ERRORS"] = "true"

    proc = subprocess.Popen(
        ["node", str(script), cfg_file, str(out_dir)],
        cwd=repo_root, env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
    )

    def _drain_err() -> None:
        assert proc.stderr is not None
        for line in proc.stderr:
            if on_line and line.strip():
                try:
                    on_line(line.rstrip("\n"))
                except Exception:
                    pass

    threading.Thread(target=_drain_err, daemon=True).start()

    history: list[str] = []
    result: dict[str, Any] = {}
    assert proc.stdout is not None and proc.stdin is not None
    for line in proc.stdout:
        line = line.strip()
        if line.startswith(OBS):
            obs = json.loads(line[len(OBS):].strip())
            try:
                action = decide(goal, obs, history)
                from orchestrator.security.agent_policy import enforce_agent_action
                action = enforce_agent_action(action, obs, initial_url=url)
            except Exception as exc:  # LLM/parse failure → end gracefully
                action = {"action": "done", "success": False, "summary": f"decider error: {str(exc)[:120]}"}
            history.append(_history_line(action))
            try:
                proc.stdin.write(json.dumps(action) + "\n")
                proc.stdin.flush()
            except BrokenPipeError:
                break
        elif line.startswith(RESULT):
            result = json.loads(line[len(RESULT):].strip())
    proc.wait(timeout=10)

    if not result:
        raise RuntimeError("ai-flow produced no result")
    result["mode"] = mode
    return result


def _history_line(action: dict[str, Any]) -> str:
    a = action.get("action", "?")
    bits = [a]
    if "i" in action:
        bits.append(str(action["i"]))
    if action.get("value") is not None:
        from orchestrator.security.redaction import redact_text
        bits.append(f"= {redact_text(str(action['value']))}")
    if action.get("reason") or action.get("summary"):
        bits.append(f"({action.get('reason') or action.get('summary')})")
    return " ".join(bits)
