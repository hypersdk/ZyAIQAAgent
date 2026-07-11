"""Playwright test generation agent."""

from __future__ import annotations

import json
import os
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


def generate_test_for_requirement(
    requirement: Requirement,
    *,
    code_context: str | None = None,
) -> str:
    """Generate Playwright TypeScript for a single requirement."""
    llm = get_llm()
    system = load_prompt("generator")

    payload = requirement.model_dump_json(indent=2)
    context_block = ""
    if code_context:
        context_block = f"\n\nCode/doc context from the product repo:\n{code_context}\n"
    elif "discovered" in requirement.tags and requirement.description:
        context_block = f"\n\nDiscovery context:\n{requirement.description}\n"

    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(
                content=(
                    f"Generate a Playwright test for this requirement:\n\n{payload}"
                    f"{context_block}\n"
                    "Output only TypeScript code."
                )
            ),
        ]
    )
    return _extract_typescript(response.content)


def generate_tests_from_requirements(
    requirements: list[Requirement],
    output_dir: str | Path,
    *,
    coverage_mode: bool = False,
) -> tuple[list[str], dict[str, int]]:
    """Generate test files for all requirements. Returns paths and quality stats."""
    from agents.generator.quality import collect_existing_hashes

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []
    stats = {"quality_passed": 0, "quality_regenerated": 0, "quality_issues": 0}
    existing_hashes = collect_existing_hashes(output_dir)

    for req in requirements:
        path, passed, issues = generate_and_validate_test(
            req,
            output_dir,
            coverage_mode=coverage_mode,
            existing_hashes=existing_hashes,
        )
        generated.append(path)
        if passed:
            stats["quality_passed"] += 1
        else:
            stats["quality_regenerated"] += 1
            stats["quality_issues"] += len(issues)
        try:
            content = Path(path).read_text(encoding="utf-8")
            existing_hashes[path] = __import__("hashlib").sha256(content.strip().encode()).hexdigest()
        except OSError:
            pass

    return generated, stats


def generate_tests_from_json(
    requirements_path: str | Path,
    output_dir: str | Path,
) -> list[str]:
    """Load requirements JSON and generate tests."""
    path = Path(requirements_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    parsed = ParsedRequirements.model_validate(data)
    generated, _ = generate_tests_from_requirements(parsed.requirements, output_dir)
    return generated


def render_template_fallback(
    requirement: Requirement,
    output_dir: str | Path,
    *,
    filename_prefix: str = "",
) -> str:
    """Fallback: render Jinja2 template when LLM is unavailable."""
    repo_root = Path(__file__).resolve().parents[2]
    env = Environment(loader=FileSystemLoader(repo_root / "templates"))
    template = env.get_template("test.spec.ts.j2")

    from agents.generator.quality import sanitize_steps

    base_url = os.environ.get("ZYVOR_BASE_URL", "https://zyvor.dev")
    dashboard_enabled = os.environ.get("ENABLE_DASHBOARD_TESTS", "false").lower() == "true"
    marketing_only = "zyvor.dev" in base_url and not dashboard_enabled

    start_path = "/"
    for step in requirement.steps:
        if step.action == "navigate" and step.target:
            start_path = step.target if step.target.startswith("/") else f"/{step.target.lstrip('/')}"
            break

    safe_steps = sanitize_steps(requirement.steps)

    code = template.render(
        title=requirement.title,
        requirement_id=requirement.id,
        steps=safe_steps,
        login_required=(
            not marketing_only
            and ("auth" in requirement.tags or "login" in requirement.tags or "dashboard" in requirement.tags)
        ),
        start_path=start_path,
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{filename_prefix}{_slugify(requirement.id)}-{_slugify(requirement.title)}.spec.ts"
    path = output_dir / filename
    path.write_text(code, encoding="utf-8")
    return str(path)


def generate_and_validate_test(
    requirement: Requirement,
    output_dir: Path,
    *,
    coverage_mode: bool = False,
    existing_hashes: dict[str, str] | None = None,
) -> tuple[str, bool, list[str]]:
    """Generate a test, run quality gate, fallback to template if needed."""
    from agents.generator.quality import check_test_quality, has_syntax_errors

    prefix = "coverage-" if coverage_mode else ""
    filename = f"{prefix}{_slugify(requirement.id)}-{_slugify(requirement.title)}.spec.ts"
    path = output_dir / filename

    try:
        code_context = requirement.description if coverage_mode else None
        code = generate_test_for_requirement(requirement, code_context=code_context)
        passed, issues = check_test_quality(code, requirement, existing_hashes=existing_hashes)
        if passed and not has_syntax_errors(code):
            path.write_text(code, encoding="utf-8")
            return str(path), True, []
    except Exception:
        issues = ["LLM generation failed"]

    fallback_path = render_template_fallback(
        requirement,
        output_dir,
        filename_prefix=prefix,
    )
    fallback_code = Path(fallback_path).read_text(encoding="utf-8")
    if has_syntax_errors(fallback_code):
        issues.append("template fallback still has syntax errors")
    passed, fallback_issues = check_test_quality(
        fallback_code, requirement, existing_hashes=existing_hashes
    )
    return fallback_path, passed, issues + fallback_issues
