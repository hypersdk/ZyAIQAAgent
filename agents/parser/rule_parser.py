"""Rule-based requirement parser — no LLM required."""

from __future__ import annotations

import re

from agents.common.models import ParsedRequirements, Requirement, RequirementStep


def _slug_id(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"req-{slug[:40]}" or "req-001"


def _normalize_path(raw: str) -> str:
    raw = raw.strip().rstrip("/")
    if raw.startswith("http"):
        match = re.search(r"https?://[^/]+(/[^?\s]*)?", raw)
        if match and match.group(1):
            return match.group(1) or "/"
        return "/"
    if not raw.startswith("/"):
        return f"/{raw}"
    return raw or "/"


def _parse_step(line: str) -> RequirementStep | None:
    line = line.strip()
    if not line:
        return None

    loads_at = re.search(
        r"(?:loads|available|opens|navigates?)\s+(?:at|to|on)\s+[`'\"]([^`'\"]+)[`'\"]",
        line,
        re.I,
    )
    if loads_at:
        return RequirementStep(action="navigate", target=_normalize_path(loads_at.group(1)))

    path_inline = re.search(r"[`'\"](/[^`'\"]+)[`'\"]", line)
    nav = re.search(r"Navigate to .+ at [`'\"]([^`'\"]+)[`'\"]", line, re.I)
    if nav:
        return RequirementStep(action="navigate", target=_normalize_path(nav.group(1)))
    if path_inline and re.search(r"navigate|route|page|loads|visit", line, re.I):
        return RequirementStep(action="navigate", target=_normalize_path(path_inline.group(1)))

    click = re.search(r'Click ["\']([^"\']+)["\']', line, re.I)
    if click:
        return RequirementStep(action="click", target=click.group(1))

    fill = re.search(r"Enter .+?: [`'\"]([^`'\"]+)[`'\"]", line, re.I)
    if fill:
        name_match = re.search(r"Enter (\w+)", line, re.I)
        return RequirementStep(
            action="fill",
            target=name_match.group(1) if name_match else "field",
            value=fill.group(1),
        )

    assert_match = re.search(r"(.+?) shows [`'\"]([^`'\"]+)[`'\"]", line, re.I)
    if assert_match:
        return RequirementStep(
            action="assert",
            target=assert_match.group(1),
            assertion=assert_match.group(2),
        )

    visible_match = re.search(
        r"(?:heading|title|text|content|button|link)\s+[`'\"]([^`'\"]+)[`'\"]\s+(?:is|are)\s+visible",
        line,
        re.I,
    )
    if visible_match:
        return RequirementStep(action="assert", target="content", assertion=visible_match.group(1))

    if re.search(r"shows .+ within", line, re.I):
        text_match = re.search(r'shows ["\']([^"\']+)["\']', line, re.I)
        if text_match:
            return RequirementStep(action="assert", assertion=text_match.group(1))

    if re.search(r"is visible|are visible|displays|contains", line, re.I):
        text_match = re.search(r'[`"\']([^`"\']+)[`"\']', line)
        if text_match:
            return RequirementStep(action="assert", assertion=text_match.group(1))

    return None


def _ensure_navigate_step(steps: list[RequirementStep]) -> list[RequirementStep]:
    if any(step.action == "navigate" for step in steps):
        return steps
    if steps:
        return [RequirementStep(action="navigate", target="/"), *steps]
    return [RequirementStep(action="navigate", target="/")]


def parse_spec_rule_based(content: str, source: str = "local") -> ParsedRequirements:
    """Parse markdown user stories without LLM."""
    lines = content.splitlines()
    title = "Untitled requirement"
    description_parts: list[str] = []
    steps: list[RequirementStep] = []
    tags: list[str] = []
    in_criteria = False
    in_tags = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("##"):
            title = stripped.lstrip("# ").strip()
            continue
        if stripped.lower().startswith("## acceptance criteria"):
            in_criteria = True
            in_tags = False
            continue
        if stripped.lower().startswith("## tags"):
            in_tags = True
            in_criteria = False
            continue
        if stripped.startswith("##"):
            in_criteria = False
            in_tags = False
            continue

        if in_criteria:
            step_line = re.sub(r"^\d+\.\s*", "", stripped)
            step = _parse_step(step_line)
            if step:
                steps.append(step)
        elif in_tags:
            tags.extend(t.strip() for t in stripped.split(",") if t.strip())
        elif stripped.startswith("**") or stripped.startswith("-"):
            description_parts.append(stripped)

    if "staging" in content.lower() or "ZYVOR_STAGING" in content:
        tags.append("vm")
    tags.append("marketing")

    steps = _ensure_navigate_step(steps)

    requirement = Requirement(
        id=_slug_id(title),
        title=title,
        description=" ".join(description_parts) or title,
        priority="high" if "smoke" in tags else "medium",
        steps=steps,
        tags=tags or ["generated"],
    )

    return ParsedRequirements(source=source, requirements=[requirement])
