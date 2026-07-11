"""Sanitize assertion text and validate generated Playwright specs."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from agents.common.models import Requirement, RequirementStep


def sanitize_assertion_text(text: str) -> str:
    """Return safe visible text for getByText, or empty if unsuitable."""
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned or len(cleaned) > 60:
        return ""
    if re.search(r"(^//|/\*|import |export |function |const |=>|\{|\}|;)", cleaned):
        return ""
    if cleaned.count("/") >= 2:
        return ""
    return cleaned


def sanitize_steps(steps: list[RequirementStep]) -> list[RequirementStep]:
    """Sanitize requirement steps before template rendering."""
    sanitized: list[RequirementStep] = []
    for step in steps:
        if step.action == "assert":
            if step.target == "heading":
                sanitized.append(
                    RequirementStep(action="assert", target="heading", assertion="heading")
                )
                continue
            safe = sanitize_assertion_text(step.assertion or step.target or "")
            if safe:
                sanitized.append(
                    RequirementStep(action="assert", target="content", assertion=safe)
                )
            else:
                sanitized.append(
                    RequirementStep(action="assert", target="heading", assertion="heading")
                )
            continue
        sanitized.append(step)
    return sanitized


def has_syntax_errors(code: str) -> bool:
    """Detect common TypeScript syntax issues in generated tests."""
    if re.search(r"getByText\(\s*/[^'\")]*//", code):
        return True
    if re.search(r"getByText\(\s*/\s*/", code):
        return True
    if code.count("(") != code.count(")"):
        return True
    if code.count("{") != code.count("}"):
        return True
    return False


def validate_spec_file(path: Path) -> bool:
    """Return True if a spec file appears syntactically valid."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return False
    if has_syntax_errors(content):
        return False
    try:
        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as tmp:
            # Strip types/imports for a coarse node syntax check
            stripped = re.sub(r"import .+;\n?", "", content)
            stripped = re.sub(r":\s*\{[^}]+\}", "", stripped)
            tmp.write(stripped)
            tmp_path = tmp.name
        result = subprocess.run(
            ["node", "--check", tmp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        Path(tmp_path).unlink(missing_ok=True)
        return result.returncode == 0
    except Exception:
        return not has_syntax_errors(content)


def _requirement_path(req: Requirement) -> str:
    for step in req.steps:
        if step.action == "navigate" and step.target:
            target = step.target.strip()
            if target.startswith("/"):
                return target
            if target.startswith("http"):
                from urllib.parse import urlparse

                return urlparse(target).path or "/"
    for tag in req.tags:
        if tag.startswith("path:"):
            return tag.split(":", 1)[1]
    return "/"


def _extract_goto_paths(code: str) -> list[str]:
    return re.findall(r"goto\(\s*['\"`]([^'\"`]+)['\"`]", code)


def check_test_quality(
    code: str,
    requirement: Requirement,
    *,
    existing_hashes: dict[str, str] | None = None,
) -> tuple[bool, list[str]]:
    """Return (passed, issues) for a generated test file."""
    issues: list[str] = []
    expected_path = _requirement_path(requirement)
    goto_paths = _extract_goto_paths(code)

    if has_syntax_errors(code):
        issues.append("TypeScript syntax error detected")

    if expected_path != "/" and goto_paths == ["/"]:
        issues.append(f"navigates to '/' but requirement path is '{expected_path}'")

    if "coverage" in requirement.tags:
        if "playwright/fixtures/base" not in code:
            issues.append("coverage test missing fixtures/base import")
        if "waitForPageReady" not in code:
            issues.append("coverage test missing waitForPageReady")
        if ".toBeAttached()" in code:
            issues.append("uses toBeAttached instead of toBeVisible")

    if ".toBeAttached()" in code and "coverage" not in requirement.tags:
        issues.append("uses brittle toBeAttached assertion")

    body_hash = hashlib.sha256(code.strip().encode()).hexdigest()
    if existing_hashes and body_hash in existing_hashes.values():
        issues.append("duplicate test body hash")

    if not goto_paths and expected_path != "/":
        issues.append("missing navigation step")

    return len(issues) == 0, issues


def collect_existing_hashes(output_dir: Path) -> dict[str, str]:
    """Map file path -> content hash for deduplication."""
    hashes: dict[str, str] = {}
    if not output_dir.exists():
        return hashes
    for path in output_dir.glob("*.spec.ts"):
        try:
            content = path.read_text(encoding="utf-8")
            hashes[str(path)] = hashlib.sha256(content.strip().encode()).hexdigest()
        except OSError:
            continue
    return hashes


def assertion_literal(text: str) -> str:
    """JSON-encode assertion text for safe Playwright string literals."""
    safe = sanitize_assertion_text(text)
    return json.dumps(safe) if safe else ""
