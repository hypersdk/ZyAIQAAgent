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

"""Ten self-contained HTTP/network probes for the dashboard."""

from __future__ import annotations

import socket
import time
from typing import Any, Callable, Optional
from urllib.parse import urljoin, urlparse

Result = dict[str, Any]
Log = Optional[Callable[[str], None]]


def _client(insecure: bool = False):
    import httpx

    return httpx.Client(timeout=15, verify=not insecure, follow_redirects=False)


def _origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


# 1 ─ redirect chain ───────────────────────────────────────────────
def redirects(url: str, log: Log = None, insecure: bool = False, **_: Any) -> Result:
    import httpx

    chain, cur, status = [], url, "ok"
    with httpx.Client(timeout=15, verify=not insecure, follow_redirects=False) as c:
        for hop in range(10):
            r = c.get(cur)
            chain.append([str(r.status_code), cur])
            if log:
                log(f"{r.status_code} {cur}")
            loc = r.headers.get("location")
            if r.status_code in (301, 302, 303, 307, 308) and loc:
                cur = urljoin(cur, loc)
            else:
                break
        else:
            status = "warn"
    hops = len(chain) - 1
    if hops > 4:
        status = "warn"
    return {
        "summary": f"{hops} redirect hop(s) → final {chain[-1][0]}",
        "status": status, "columns": ["status", "url"], "rows": chain, "issues": [],
    }


# 2 ─ full header inspector ────────────────────────────────────────
def headers(url: str, log: Log = None, insecure: bool = False, **_: Any) -> Result:
    with _client(insecure=insecure) as c:
        r = c.get(url)
    rows = [[k, v] for k, v in sorted(r.headers.items())]
    if log:
        log(f"{r.status_code} — {len(rows)} headers")
    return {
        "summary": f"HTTP {r.status_code} · {r.http_version} · {len(rows)} headers",
        "status": "ok" if r.status_code < 400 else "fail",
        "columns": ["header", "value"], "rows": rows, "issues": [],
    }


# 3 ─ cookie audit ─────────────────────────────────────────────────
def cookies(url: str, log: Log = None, insecure: bool = False, **_: Any) -> Result:
    with _client(insecure=insecure) as c:
        r = c.get(url)
    raw = r.headers.get_list("set-cookie") if hasattr(r.headers, "get_list") else []
    if not raw and "set-cookie" in r.headers:
        raw = [r.headers["set-cookie"]]
    rows, issues = [], []
    for sc in raw:
        name = sc.split("=", 1)[0]
        low = sc.lower()
        samesite = "samesite" in low
        rows.append([name, "✓" if "secure" in low else "✗", "✓" if "httponly" in low else "✗", "✓" if samesite else "✗"])
        if "secure" not in low:
            issues.append(f"{name}: not Secure")
        if "httponly" not in low:
            issues.append(f"{name}: not HttpOnly")
        if not samesite:
            issues.append(f"{name}: no SameSite")
    if log:
        log(f"{len(rows)} cookie(s), {len(issues)} issue(s)")
    return {
        "summary": f"{len(rows)} cookie(s) · {len(issues)} flag(s)",
        "status": "fail" if issues else "ok",
        "columns": ["cookie", "Secure", "HttpOnly", "SameSite"], "rows": rows, "issues": issues,
    }


# 4 ─ robots.txt + sitemap ─────────────────────────────────────────
def robots(url: str, log: Log = None, insecure: bool = False, **_: Any) -> Result:
    origin = _origin(url)
    rows, issues = [], []
    with _client(insecure=insecure) as c:
        for path in ("/robots.txt", "/sitemap.xml"):
            try:
                r = c.get(origin + path, follow_redirects=True)
                present = r.status_code < 400
                detail = ""
                if present and path == "/robots.txt":
                    detail = f"{len(r.text.splitlines())} lines"
                elif present and path == "/sitemap.xml":
                    detail = f"{r.text.count('<loc>')} urls"
                rows.append([path, str(r.status_code), detail])
                if not present:
                    issues.append(f"{path} missing ({r.status_code})")
            except Exception as exc:
                rows.append([path, "ERR", str(exc)[:40]])
                issues.append(f"{path}: {exc}")
    if log:
        log("robots/sitemap checked")
    return {
        "summary": f"{'both present' if not issues else 'missing files'}",
        "status": "warn" if issues else "ok",
        "columns": ["path", "status", "detail"], "rows": rows, "issues": issues,
    }


# 5 ─ sensitive path exposure ──────────────────────────────────────
def security_paths(url: str, log: Log = None, insecure: bool = False, **_: Any) -> Result:
    origin = _origin(url)
    probe = ["/.env", "/.git/config", "/.htaccess", "/config.json", "/backup.sql", "/.aws/credentials", "/wp-config.php"]
    rows, exposed = [], []
    with _client(insecure=insecure) as c:
        for p in probe:
            try:
                r = c.get(origin + p)
                ctype = r.headers.get("content-type", "").lower()
                # An SPA serves index.html (text/html) for every path — that's a
                # fallback, not an exposed file. Only flag real file content.
                is_html = "text/html" in ctype
                hit = r.status_code == 200 and len(r.content) > 0 and not is_html
                verdict = "⚠ EXPOSED" if hit else ("ok (SPA fallback)" if r.status_code == 200 and is_html else "ok")
                rows.append([p, str(r.status_code), verdict])
                if hit:
                    exposed.append(p)
                if log:
                    log(f"{r.status_code} {p}{' EXPOSED' if hit else ''}")
            except Exception:
                rows.append([p, "ERR", ""])
    return {
        "summary": f"{len(exposed)} exposed of {len(probe)} sensitive paths",
        "status": "fail" if exposed else "ok",
        "columns": ["path", "status", "verdict"], "rows": rows,
        "issues": [f"exposed: {p}" for p in exposed],
    }


# 6 ─ API JSON check ───────────────────────────────────────────────
def api_check(
    url: str,
    expect_status: int = 200,
    json_path: str = "",
    contains: str = "",
    log: Log = None,
    insecure: bool = False,
    **_: Any,
) -> Result:
    import httpx

    t0 = time.time()
    with httpx.Client(timeout=15, verify=not insecure, follow_redirects=True) as c:
        r = c.get(url)
    ms = round((time.time() - t0) * 1000)
    issues, rows = [], [["status", str(r.status_code)], ["latency", f"{ms}ms"], ["content-type", r.headers.get("content-type", "")]]
    if r.status_code != expect_status:
        issues.append(f"status {r.status_code} ≠ expected {expect_status}")
    body = None
    try:
        body = r.json()
        rows.append(["json", "valid"])
    except Exception:
        if json_path or contains:
            issues.append("response is not valid JSON")
    if json_path and isinstance(body, (dict, list)):
        val: Any = body
        try:
            for key in json_path.split("."):
                val = val[int(key)] if isinstance(val, list) else val[key]
            rows.append([json_path, str(val)[:80]])
            if contains and contains not in str(val):
                issues.append(f"{json_path} does not contain '{contains}'")
        except Exception:
            issues.append(f"json path '{json_path}' not found")
    if log:
        log(f"{r.status_code} in {ms}ms")
    return {
        "summary": f"HTTP {r.status_code} · {ms}ms · {len(issues)} issue(s)",
        "status": "fail" if issues else "ok",
        "columns": ["field", "value"], "rows": rows, "issues": issues,
    }


# 7 ─ sitemap URL tester ───────────────────────────────────────────
def sitemap_test(url: str, log: Log = None, insecure: bool = False, **_: Any) -> Result:
    import re

    origin = _origin(url)
    with _client(insecure=insecure) as c:
        try:
            sm = c.get(origin + "/sitemap.xml", follow_redirects=True)
        except Exception as exc:
            raise RuntimeError(f"sitemap fetch failed: {exc}")
        if sm.status_code >= 400:
            raise RuntimeError(f"no sitemap.xml ({sm.status_code})")
        urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm.text)[:40]
        rows, bad = [], []
        for u in urls:
            try:
                r = c.get(u, follow_redirects=True)
                rows.append([str(r.status_code), u])
                if r.status_code >= 400:
                    bad.append(f"{r.status_code} {u}")
                if log:
                    log(f"{r.status_code} {u}")
            except Exception:
                rows.append(["ERR", u])
                bad.append(f"ERR {u}")
    return {
        "summary": f"{len(urls)} sitemap URLs · {len(bad)} broken",
        "status": "fail" if bad else "ok",
        "columns": ["status", "url"], "rows": rows, "issues": bad,
    }


# 8 ─ DNS records ──────────────────────────────────────────────────
def dns_records(host: str, log: Log = None, **_: Any) -> Result:
    if host.startswith(("http://", "https://")):
        host = urlparse(host).hostname or host
    rows, issues = [], []
    try:
        v4 = sorted({i[4][0] for i in socket.getaddrinfo(host, None, socket.AF_INET)})
    except Exception:
        v4 = []
    try:
        v6 = sorted({i[4][0] for i in socket.getaddrinfo(host, None, socket.AF_INET6)})
    except Exception:
        v6 = []
    for ip in v4:
        rows.append(["A", ip])
    for ip in v6:
        rows.append(["AAAA", ip])
    for ip in v4[:3]:
        try:
            ptr = socket.gethostbyaddr(str(ip))[0]
            rows.append(["PTR", f"{ip} → {ptr}"])
        except Exception:
            pass
    if not v4 and not v6:
        issues.append("no A/AAAA records — host does not resolve")
    if log:
        log(f"{host}: {len(v4)} A, {len(v6)} AAAA")
    return {
        "summary": f"{len(v4)} A · {len(v6)} AAAA record(s)",
        "status": "fail" if issues else "ok",
        "columns": ["type", "value"], "rows": rows, "issues": issues,
    }


# 9 ─ CORS check ───────────────────────────────────────────────────
def cors(url: str, log: Log = None, insecure: bool = False, **_: Any) -> Result:
    import httpx

    with httpx.Client(timeout=15, verify=not insecure) as c:
        r = c.get(url, headers={"Origin": "https://example.com"})
    acao = r.headers.get("access-control-allow-origin", "")
    acac = r.headers.get("access-control-allow-credentials", "")
    rows = [
        ["Access-Control-Allow-Origin", acao or "(none)"],
        ["Access-Control-Allow-Credentials", acac or "(none)"],
        ["Access-Control-Allow-Methods", r.headers.get("access-control-allow-methods", "(none)")],
    ]
    issues = []
    if acao == "*" and acac.lower() == "true":
        issues.append("wildcard origin with credentials — insecure CORS")
    if log:
        log(f"ACAO: {acao or 'none'}")
    return {
        "summary": f"CORS {'permissive' if acao == '*' else acao or 'not set'}",
        "status": "fail" if issues else "ok",
        "columns": ["header", "value"], "rows": rows, "issues": issues,
    }


# 10 ─ compression / caching / protocol ────────────────────────────
def transport(url: str, log: Log = None, insecure: bool = False, **_: Any) -> Result:
    import httpx

    with httpx.Client(timeout=15, verify=not insecure, follow_redirects=True) as c:
        r = c.get(url, headers={"Accept-Encoding": "gzip, br"})
    enc = r.headers.get("content-encoding", "")
    cache = r.headers.get("cache-control", "")
    rows = [
        ["HTTP version", r.http_version],
        ["content-encoding", enc or "(none)"],
        ["cache-control", cache or "(none)"],
        ["content-length", r.headers.get("content-length", "?")],
        ["server", r.headers.get("server", "(hidden)")],
    ]
    issues = []
    if not enc:
        issues.append("no compression (gzip/br) — larger transfers")
    if not cache:
        issues.append("no cache-control header")
    if log:
        log(f"{r.http_version} · {enc or 'no'} compression")
    return {
        "summary": f"{r.http_version} · {enc or 'uncompressed'}",
        "status": "warn" if issues else "ok",
        "columns": ["field", "value"], "rows": rows, "issues": issues,
    }


PROBES: dict[str, Callable[..., Result]] = {
    "redirects": redirects,
    "headers": headers,
    "cookies": cookies,
    "robots": robots,
    "security_paths": security_paths,
    "api_check": api_check,
    "sitemap_test": sitemap_test,
    "dns_records": dns_records,
    "cors": cors,
    "transport": transport,
}
