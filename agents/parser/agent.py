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

"""Requirement parsing agent."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import LLMConfigError, content_to_text, get_llm, load_prompt
from agents.common.models import ParsedRequirements, Requirement
from agents.parser.rule_parser import parse_spec_rule_based


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences."""
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence_match:
        text = fence_match.group(1)
    return json.loads(text)


def _llm_available() -> bool:
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "azure": "AZURE_OPENAI_API_KEY",
    }
    if provider == "ollama":
        return True
    key = key_map.get(provider, "OPENAI_API_KEY")
    return bool(os.environ.get(key))


def parse_spec_content(content: str, source: str = "local") -> ParsedRequirements:
    """Parse a spec — LLM when configured, rule-based fallback otherwise."""
    if not _llm_available():
        return parse_spec_rule_based(content, source=source)

    try:
        llm = get_llm()
        system = load_prompt("parser")
        response = llm.invoke(
            [
                SystemMessage(content=system),
                HumanMessage(content=f"Parse the following specification:\n\n{content}"),
            ]
        )
        raw = _extract_json(content_to_text(response.content))
        requirements = [Requirement.model_validate(r) for r in raw.get("requirements", [])]
        return ParsedRequirements(source=source, requirements=requirements)
    except (LLMConfigError, json.JSONDecodeError, ValueError, Exception):
        return parse_spec_rule_based(content, source=source)


def parse_spec_file(path: str | Path) -> ParsedRequirements:
    """Parse a local markdown spec file."""
    path = Path(path)
    content = path.read_text(encoding="utf-8")
    return parse_spec_content(content, source=str(path))


def save_requirements(parsed: ParsedRequirements, output_path: str | Path) -> Path:
    """Persist parsed requirements to JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        parsed.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return output_path
