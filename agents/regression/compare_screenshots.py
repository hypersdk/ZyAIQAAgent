"""Screenshot regression comparison — Phase 2 stub."""

from __future__ import annotations

from pathlib import Path


def compare_screenshots(
    baseline_dir: str | Path,
    current_dir: str | Path,
    threshold: float = 0.01,
) -> list[dict]:
    """
    Compare screenshots between baseline and current runs.

    Phase 2: integrate pixelmatch or similar.
    Returns list of diffs with paths and diff percentages.
    """
    baseline_dir = Path(baseline_dir)
    current_dir = Path(current_dir)

    if not baseline_dir.exists() or not current_dir.exists():
        return []

    diffs: list[dict] = []
    for current in current_dir.glob("*.png"):
        baseline = baseline_dir / current.name
        if baseline.exists():
            diffs.append(
                {
                    "file": current.name,
                    "status": "pending",
                    "message": "Screenshot diff not implemented (Phase 2)",
                }
            )
    return diffs
