"""Playwright test generation agent."""

from __future__ import annotations

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage, SystemMessage

from agents.common.llm import get_llm, load_prompt
from agents.common.models import ParsedRequirements, Requirement


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "test"


def _extract_typescript(text: str) -> str:
    """Extract TypeScript code from LLM response."""
    text = text.strip()
    fence_match = re.search(r"```(?:typescript|ts)?\s*([\s\S]*?)\s*```", text)
    if fence_match:
        return fence_match.group(1).strip()
    if "import" in text and "test(" in text:
        return text
    raise ValueError("LLM did not return valid TypeScript test code")


def generate_test_for_requirement(requirement: Requirement) -> str:
    """Generate Playwright TypeScript for a single requirement."""
    llm = get_llm()
    system = load_prompt("generator")

    payload = requirement.model_dump_json(indent=2)
    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(
                content=(
                    f"Generate a Playwright test for this requirement:\n\n{payload}\n\n"
                    "Output only TypeScript code."
                )
            ),
        ]
    )
    return _extract_typescript(response.content)


def generate_tests_from_requirements(
    requirements: list[Requirement],
    output_dir: str | Path,
) -> list[str]:
    """Generate test files for all requirements. Returns list of file paths."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []

    for req in requirements:
        code = generate_test_for_requirement(req)
        filename = f"{_slugify(req.id)}-{_slugify(req.title)}.spec.ts"
        path = output_dir / filename
        path.write_text(code, encoding="utf-8")
        generated.append(str(path))

    return generated


def generate_tests_from_json(
    requirements_path: str | Path,
    output_dir: str | Path,
) -> list[str]:
    """Load requirements JSON and generate tests."""
    path = Path(requirements_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    parsed = ParsedRequirements.model_validate(data)
    return generate_tests_from_requirements(parsed.requirements, output_dir)


def render_template_fallback(requirement: Requirement, output_dir: str | Path) -> str:
    """Fallback: render Jinja2 template when LLM is unavailable."""
    repo_root = Path(__file__).resolve().parents[2]
    env = Environment(loader=FileSystemLoader(repo_root / "templates"))
    template = env.get_template("test.spec.ts.j2")

    code = template.render(
        title=requirement.title,
        requirement_id=requirement.id,
        steps=requirement.steps,
        login_required="auth" in requirement.tags or "login" in requirement.tags,
        start_path=requirement.steps[0].target if requirement.steps else "/",
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{_slugify(requirement.id)}-{_slugify(requirement.title)}.spec.ts"
    path = output_dir / filename
    path.write_text(code, encoding="utf-8")
    return str(path)
