"""Requirement parsing agent."""

from __future__ import annotations

import json
import re
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import get_llm, load_prompt
from agents.common.models import ParsedRequirements, Requirement


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences."""
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence_match:
        text = fence_match.group(1)
    return json.loads(text)


def parse_spec_content(content: str, source: str = "local") -> ParsedRequirements:
    """Parse a single spec markdown string into structured requirements."""
    llm = get_llm()
    system = load_prompt("parser")

    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=f"Parse the following specification:\n\n{content}"),
        ]
    )
    raw = _extract_json(response.content)
    requirements = [Requirement.model_validate(r) for r in raw.get("requirements", [])]
    return ParsedRequirements(source=source, requirements=requirements)


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
