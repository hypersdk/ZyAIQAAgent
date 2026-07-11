"""Heuristic coverage discovery from docs and code signals."""

from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

from agents.common.models import CoverageCandidate


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "item"


def _dedupe(candidates: list[CoverageCandidate]) -> list[CoverageCandidate]:
    seen: set[str] = set()
    unique: list[CoverageCandidate] = []
    for candidate in candidates:
        key = f"{candidate.kind}:{candidate.path}:{candidate.title}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def _extract_markdown_pages(content: str, source_file: str) -> list[CoverageCandidate]:
    candidates: list[CoverageCandidate] = []
    for line in content.splitlines():
        match = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        if level == 1 and title.lower() in {"readme", "changelog"}:
            continue
        path = f"/{ _slug(title) }"
        candidates.append(
            CoverageCandidate(
                id=f"doc-{_slug(source_file)}-{_slug(title)}",
                kind="doc" if level > 1 else "page",
                path=path,
                title=title,
                signals=[f"markdown-h{level}", source_file],
                priority="high" if level <= 2 else "medium",
                source_file=source_file,
                context=line.strip(),
            )
        )
    return candidates


def _extract_sidebar_entries(content: str, source_file: str) -> list[CoverageCandidate]:
    candidates: list[CoverageCandidate] = []
    for match in re.finditer(r"id:\s*['\"]([^'\"]+)['\"]", content):
        doc_id = match.group(1)
        path = f"/{doc_id}" if not doc_id.startswith("/") else doc_id
        candidates.append(
            CoverageCandidate(
                id=f"sidebar-{_slug(doc_id)}",
                kind="page",
                path=path,
                title=doc_id.replace("/", " ").replace("-", " ").title(),
                signals=["sidebar-id", source_file],
                priority="high",
                source_file=source_file,
                context=match.group(0),
            )
        )
    for match in re.finditer(r"label:\s*['\"]([^'\"]+)['\"]", content):
        label = match.group(1)
        candidates.append(
            CoverageCandidate(
                id=f"sidebar-label-{_slug(label)}",
                kind="page",
                path=f"/{_slug(label)}",
                title=label,
                signals=["sidebar-label", source_file],
                priority="medium",
                source_file=source_file,
                context=match.group(0),
            )
        )
    return candidates


def _route_from_page_file(repo_path: str) -> str | None:
    normalized = repo_path.replace("\\", "/")
    for prefix in ("src/pages/", "src/routes/", "app/", "pages/"):
        if prefix in normalized:
            rel = normalized.split(prefix, 1)[1]
            rel = re.sub(r"\.(tsx|ts|jsx|js)$", "", rel)
            rel = rel.replace("/index", "")
            if rel in {"", "index"}:
                return "/"
            return f"/{rel}"
    return None


def _extract_route_files(repo_path: str, content: str) -> list[CoverageCandidate]:
    route = _route_from_page_file(repo_path)
    if not route:
        return []

    title = Path(repo_path).stem.replace("-", " ").replace("_", " ").title()
    return [
        CoverageCandidate(
            id=f"route-{_slug(route)}",
            kind="route",
            path=route,
            title=title,
            signals=["route-file", repo_path],
            priority="high",
            source_file=repo_path,
            context=content[:500],
        )
    ]


def _extract_openapi_paths(content: str, source_file: str) -> list[CoverageCandidate]:
    candidates: list[CoverageCandidate] = []
    spec: dict | None = None
    try:
        if source_file.endswith((".yaml", ".yml")):
            if yaml is None:
                return candidates
            spec = yaml.safe_load(content)
        else:
            spec = json.loads(content)
    except Exception:
        return candidates

    if not isinstance(spec, dict):
        return candidates

    paths = spec.get("paths", {})
    if not isinstance(paths, dict):
        return candidates

    for api_path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        title = f"{list(methods.keys())[0].upper()} {api_path}" if methods else api_path
        candidates.append(
            CoverageCandidate(
                id=f"api-{_slug(api_path)}",
                kind="api",
                path=api_path,
                title=title,
                signals=["openapi", source_file],
                priority="medium",
                source_file=source_file,
                context=str(methods)[:500],
            )
        )
    return candidates


def discover_from_file(repo_path: str, content: str) -> list[CoverageCandidate]:
    """Extract coverage candidates from a single file."""
    lower = repo_path.lower()
    candidates: list[CoverageCandidate] = []

    if lower.endswith(".md"):
        candidates.extend(_extract_markdown_pages(content, repo_path))
    if "sidebar" in Path(repo_path).name.lower():
        candidates.extend(_extract_sidebar_entries(content, repo_path))
    if lower.endswith((".tsx", ".ts", ".jsx", ".js")):
        candidates.extend(_extract_route_files(repo_path, content))
    if "openapi" in Path(repo_path).name.lower() or lower.endswith((".yaml", ".yml", ".json")):
        candidates.extend(_extract_openapi_paths(content, repo_path))

    return candidates


def discover_from_files(file_map: dict[str, str]) -> list[CoverageCandidate]:
    """Discover coverage inventory from repo_path → content mapping."""
    candidates: list[CoverageCandidate] = []
    for repo_path, content in file_map.items():
        candidates.extend(discover_from_file(repo_path, content))
    return _dedupe(candidates)


def discover_from_local_dir(local_dir: str | Path) -> list[CoverageCandidate]:
    """Discover from downloaded local fixtures."""
    local_dir = Path(local_dir)
    if not local_dir.exists():
        return []

    file_map: dict[str, str] = {}
    for path in local_dir.iterdir():
        if not path.is_file():
            continue
        repo_path = path.name.replace("__", "/")
        try:
            file_map[repo_path] = path.read_text(encoding="utf-8")
        except Exception:
            continue
    return discover_from_files(file_map)
