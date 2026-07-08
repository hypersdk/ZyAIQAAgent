"""Rust-powered screenshot diff bridge."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from agents.common.models import RegressionDiff


def rust_diff_available() -> bool:
    binary = _find_binary()
    return binary is not None and binary.exists()


def _find_binary() -> Path | None:
    repo = Path(__file__).resolve().parents[2]
    candidates = [
        repo / "rust" / "target" / "release" / "zyvor-diff",
        repo / "rust" / "target" / "debug" / "zyvor-diff",
        Path(os.environ.get("ZYVOR_DIFF_BINARY", "")),
    ]
    for c in candidates:
        if c and c.exists():
            return c
    return None


def compare_with_rust(
    baseline: Path,
    current: Path,
    diff_output: Path,
    threshold: float = 1.0,
) -> RegressionDiff:
    """Run Rust zyvor-diff binary for fast image comparison."""
    binary = _find_binary()
    if not binary:
        return RegressionDiff(
            file=current.name,
            status="fail",
            message="Rust zyvor-diff binary not found. Run: cd rust && cargo build --release",
        )

    result = subprocess.run(
        [
            str(binary),
            "--baseline", str(baseline),
            "--current", str(current),
            "--diff-output", str(diff_output),
            "--threshold", str(threshold),
        ],
        capture_output=True,
        text=True,
    )

    try:
        data = json.loads(result.stdout.strip().split("\n")[-1])
        return RegressionDiff(
            file=current.name,
            status="pass" if data["passed"] else "fail",
            diff_percent=data["diff_percent"],
            diff_image_path=str(diff_output),
            message=None if data["passed"] else f"Rust diff {data['diff_percent']:.2f}%",
        )
    except (json.JSONDecodeError, KeyError, IndexError):
        return RegressionDiff(
            file=current.name,
            status="fail",
            message=result.stderr or "Rust diff failed",
        )
