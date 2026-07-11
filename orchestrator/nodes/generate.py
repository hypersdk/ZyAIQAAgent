"""Generate Playwright tests from requirements."""

from __future__ import annotations

import os
from pathlib import Path

from agents.common.models import Requirement
from agents.generator.agent import generate_and_validate_test, render_template_fallback
from agents.generator.quality import collect_existing_hashes
from orchestrator.state import PipelineState


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_coverage_requirement(req: Requirement) -> bool:
    return "coverage" in req.tags


def _generate_batch(
    requirements: list[Requirement],
    output_dir: Path,
    *,
    coverage_mode: bool = False,
) -> tuple[list[str], dict[str, int]]:
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
            import hashlib

            existing_hashes[path] = hashlib.sha256(content.strip().encode()).hexdigest()
        except OSError:
            pass

    return generated, stats


def generate_tests(state: PipelineState) -> PipelineState:
    """Generate Playwright test files."""
    requirements = state.get("requirements", [])
    if not requirements:
        return {**state, "generated_tests": []}

    output_dir = _repo_root() / "tests" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    story_requirements = [req for req in requirements if not _is_coverage_requirement(req)]
    coverage_requirements = [req for req in requirements if _is_coverage_requirement(req)]

    max_new = int(os.environ.get("COVERAGE_MAX_NEW_TESTS", "10"))
    coverage_requirements = coverage_requirements[:max_new]

    generated: list[str] = []
    quality_stats = {"quality_passed": 0, "quality_regenerated": 0, "quality_issues": 0}

    if story_requirements:
        try:
            paths, stats = _generate_batch(story_requirements, output_dir)
            generated.extend(paths)
            for key in quality_stats:
                quality_stats[key] += stats.get(key, 0)
        except Exception:
            for req in story_requirements:
                path = render_template_fallback(req, output_dir)
                generated.append(path)

    if coverage_requirements:
        try:
            paths, stats = _generate_batch(coverage_requirements, output_dir, coverage_mode=True)
            generated.extend(paths)
            for key in quality_stats:
                quality_stats[key] += stats.get(key, 0)
        except Exception:
            for req in coverage_requirements:
                path = render_template_fallback(req, output_dir, filename_prefix="coverage-")
                generated.append(path)

    metadata = dict(state.get("metadata", {}))
    metadata["coverage_tests_generated"] = len(
        [path for path in generated if "coverage-" in Path(path).name]
    )
    metadata.update(quality_stats)

    return {**state, "generated_tests": generated, "metadata": metadata}
