"""Natural language test creation agent."""

from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import get_llm, load_prompt
from agents.common.models import ParsedRequirements, Requirement
from agents.generator.agent import generate_tests_from_requirements


def _extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1)
    return json.loads(text)


def create_from_natural_language(description: str) -> ParsedRequirements:
    """Convert a natural language description into structured requirements."""
    llm = get_llm()
    system = load_prompt("nl_create")

    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=f"Create a test requirement for:\n\n{description}"),
        ]
    )

    raw = _extract_json(response.content)
    requirements = [Requirement.model_validate(r) for r in raw.get("requirements", [])]
    return ParsedRequirements(source="natural_language", requirements=requirements)


def create_and_generate(description: str, output_dir: str) -> list[str]:
    """NL description → requirements → Playwright tests."""
    parsed = create_from_natural_language(description)
    return generate_tests_from_requirements(parsed.requirements, output_dir)
