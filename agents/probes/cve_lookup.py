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

"""Read-only CVE lookup — the narrow, non-destructive first increment of the
"active exploitation" feature bucket. Reuses
`agents.probes.misconfig_scan.fingerprint_tech`'s version extraction, then
checks each identified product/version against OSV.dev's free, keyless
vulnerability database. No PoC is generated or run; see ROADMAP.md for why
PoC generation/execution and attack chaining are deliberately out of scope.

OSV.dev is ecosystem-based (npm/PyPI/Go/...), not a generic CPE database — so
only products with a known ecosystem mapping (`_ECOSYSTEM_HINTS`) are queried;
everything else is reported as "no known ecosystem mapping" rather than
silently guessing. NVD's CPE-based search (broader coverage, needs an API key
for usable rate limits) is a documented future option behind `NVD_API_KEY`.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from agents.probes.misconfig_scan import fingerprint_tech

Log = Optional[Callable[[str], None]]

_ECOSYSTEM_HINTS: dict[str, str] = {
    "jquery": "npm",
    # WordPress core is deliberately NOT mapped here: OSV.dev's "WordPress"
    # ecosystem indexes plugins/themes by their slug, not WordPress core by
    # the literal name "wordpress" — querying it that way returns a 400
    # (confirmed against the live API), which would show up as a confusing
    # per-product "error" instead of the honest "no known ecosystem mapping"
    # note. Revisit once there's a real core-version -> advisory source.
}

_OSV_QUERY_URL = "https://api.osv.dev/v1/query"

_GHSA_SEVERITY_MAP = {"critical": "critical", "high": "high", "moderate": "medium", "low": "low"}


def identify_versions(url: str, *, insecure: bool = False, log: Log = None) -> list[dict[str, str]]:
    if log:
        log(f"cve_lookup: fingerprinting {url}")
    return fingerprint_tech(url, insecure=insecure).get("versions", [])


def _finding_severity(vuln: dict[str, Any]) -> str:
    raw = str((vuln.get("database_specific") or {}).get("severity", "")).lower()
    return _GHSA_SEVERITY_MAP.get(raw, "medium")


def lookup_vulnerabilities(product: str, version: str, *, insecure: bool = False) -> dict[str, Any]:
    """Query OSV.dev for known advisories affecting `product`@`version`."""
    ecosystem = _ECOSYSTEM_HINTS.get(product.lower())
    if not ecosystem:
        return {
            "product": product, "version": version, "ecosystem": None,
            "matches": [], "note": "no known ecosystem mapping — skipped",
        }
    import httpx

    try:
        with httpx.Client(timeout=15, verify=not insecure) as c:
            response = c.post(
                _OSV_QUERY_URL,
                json={"version": version, "package": {"name": product.lower(), "ecosystem": ecosystem}},
            )
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        return {
            "product": product, "version": version, "ecosystem": ecosystem,
            "matches": [], "error": str(exc)[:200],
        }

    matches = [
        {
            "id": vuln.get("id", ""),
            "summary": (vuln.get("summary") or vuln.get("details") or "")[:300],
            "severity": _finding_severity(vuln),
            "url": f"https://osv.dev/vulnerability/{vuln.get('id', '')}",
        }
        for vuln in data.get("vulns", []) or []
    ]
    return {"product": product, "version": version, "ecosystem": ecosystem, "matches": matches}


def run_cve_lookup(url: str, *, insecure: bool = False, log: Log = None) -> dict[str, Any]:
    versions = identify_versions(url, insecure=insecure, log=log)
    results = []
    for item in versions:
        if log:
            log(f"cve_lookup: checking {item['product']} {item['version']}")
        results.append(lookup_vulnerabilities(item["product"], item["version"], insecure=insecure))
    total_matches = sum(len(r.get("matches", [])) for r in results)
    return {"url": url, "identified": versions, "results": results, "total_matches": total_matches}
