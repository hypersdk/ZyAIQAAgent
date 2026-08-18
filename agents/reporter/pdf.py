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

"""HTML to PDF conversion for QA reports."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _repo_root() -> Path:
    from orchestrator.paths import repo_root

    return repo_root()


def html_to_pdf(html_path: Path, pdf_path: Optional[Path] = None) -> Optional[Path]:
    """Render HTML report to PDF via Playwright. Returns path on success, None on failure."""
    html_path = Path(html_path).resolve()
    if not html_path.is_file():
        logger.warning("HTML report not found: %s", html_path)
        return None

    if pdf_path is None:
        pdf_path = html_path.with_suffix(".pdf")
    else:
        pdf_path = Path(pdf_path)

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    script = _repo_root() / "playwright" / "scripts" / "html-to-pdf.mjs"

    try:
        subprocess.run(
            ["node", str(script), str(html_path), str(pdf_path)],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(_repo_root()),
        )
    except FileNotFoundError:
        logger.warning("Node.js not found; skipping PDF report generation")
        return None
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or exc.stdout or "").strip()
        logger.warning("PDF generation failed: %s", stderr or exc)
        return None

    if not pdf_path.is_file():
        logger.warning("PDF file was not created: %s", pdf_path)
        return None

    return pdf_path
