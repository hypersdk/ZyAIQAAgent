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

"""Natural language test creation agent."""

from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import content_to_text, get_llm, load_prompt
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

    raw = _extract_json(content_to_text(response.content))
    requirements = [Requirement.model_validate(r) for r in raw.get("requirements", [])]
    return ParsedRequirements(source="natural_language", requirements=requirements)


def create_from_natural_language_heuristic(description: str) -> ParsedRequirements:
    """No-LLM fallback: build a navigate + assert requirement from plain English.

    Extracts the first URL path (e.g. /vm) as the navigation target and any
    quoted strings or Capitalized phrases as visibility assertions.
    """
    from agents.common.models import RequirementStep

    text = description.strip()
    path_match = re.search(r"(?<![\w.])(/[a-z0-9][a-z0-9\-/]*)", text, re.I)
    path = path_match.group(1) if path_match else "/"

    assertions = re.findall(r"[\"'“]([^\"'”]{2,60})[\"'”]", text)
    if not assertions:
        # Capitalized multi-word phrases ("Schedule Demo", "HyperSDK") often name UI text
        assertions = re.findall(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)+)\b", text)
    if not assertions:
        assertions = re.findall(r"\b([A-Z][a-zA-Z0-9]{3,})\b", text)

    steps = [RequirementStep(action="navigate", target=path), RequirementStep(action="wait")]
    for assertion in assertions[:3]:
        steps.append(RequirementStep(action="assert", target="content", assertion=assertion.strip()))
    if len(steps) == 2:
        steps.append(RequirementStep(action="assert", target="heading", assertion="heading"))

    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "nl-test"
    requirement = Requirement(
        id=f"nl-{slug}",
        title=text[:80],
        description=text,
        priority="medium",
        steps=steps,
        tags=["nl-generated", "heuristic"],
    )
    return ParsedRequirements(source="natural_language", requirements=[requirement])


def create_and_generate(description: str, output_dir: str) -> list[str]:
    """NL description → requirements → Playwright tests."""
    parsed = create_from_natural_language(description)
    generated, _ = generate_tests_from_requirements(parsed.requirements, output_dir)
    return generated
