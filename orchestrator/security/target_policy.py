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

"""SSRF-resistant target validation for all browser, API and network jobs."""

from __future__ import annotations

import fnmatch
import ipaddress
import os
import socket
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit


class TargetPolicyError(ValueError):
    """Raised when a requested test target violates policy."""


_METADATA_HOSTS = {
    "metadata.google.internal",
    "metadata.google",
    "instance-data.ec2.internal",
}
_METADATA_IPS = {
    ipaddress.ip_address("169.254.169.254"),
    ipaddress.ip_address("169.254.170.2"),
    ipaddress.ip_address("100.100.100.200"),
}


def _csv(name: str) -> list[str]:
    return [v.strip() for v in os.environ.get(name, "").split(",") if v.strip()]


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    return default if raw is None else raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class TargetPolicy:
    allowed_hosts: tuple[str, ...] = ()
    allowed_cidrs: tuple[ipaddress._BaseNetwork, ...] = ()
    allowed_ports: tuple[int, ...] = (80, 443)
    allow_private: bool = False
    allow_http: bool = True
    resolve_dns: bool = True
    max_url_length: int = 2048
    blocked_hosts: tuple[str, ...] = field(default_factory=lambda: tuple(sorted(_METADATA_HOSTS)))

    @classmethod
    def from_env(cls) -> "TargetPolicy":
        ports = tuple(int(p) for p in _csv("ZYVOR_TARGET_ALLOWED_PORTS") or ["80", "443"])
        cidrs: list[ipaddress._BaseNetwork] = []
        for raw in _csv("ZYVOR_TARGET_ALLOWED_CIDRS"):
            cidrs.append(ipaddress.ip_network(raw, strict=False))
        env = os.environ.get("ZYVOR_ENV", "development").lower()
        allow_private = _truthy("ZYVOR_ALLOW_PRIVATE_TARGETS", default=env != "production")
        return cls(
            allowed_hosts=tuple(h.lower().rstrip(".") for h in _csv("ZYVOR_TARGET_ALLOWLIST")),
            allowed_cidrs=tuple(cidrs),
            allowed_ports=ports,
            allow_private=allow_private,
            allow_http=_truthy("ZYVOR_ALLOW_HTTP_TARGETS", default=env != "production"),
            resolve_dns=not _truthy("ZYVOR_SKIP_TARGET_DNS_RESOLUTION", default=False),
        )

    def validate_url(self, raw_url: str) -> str:
        if not isinstance(raw_url, str) or not raw_url.strip():
            raise TargetPolicyError("target URL is required")
        raw_url = raw_url.strip()
        if len(raw_url) > self.max_url_length:
            raise TargetPolicyError("target URL is too long")

        parsed = urlsplit(raw_url)
        if parsed.scheme not in {"http", "https"}:
            raise TargetPolicyError("target scheme must be http or https")
        if parsed.scheme == "http" and not self.allow_http:
            raise TargetPolicyError("plain HTTP targets are disabled")
        if parsed.username or parsed.password:
            raise TargetPolicyError("credentials must not be embedded in target URLs")
        if not parsed.hostname:
            raise TargetPolicyError("target hostname is required")

        host = parsed.hostname.lower().rstrip(".")
        if host in self.blocked_hosts or host.endswith(".internal") and "metadata" in host:
            raise TargetPolicyError("cloud metadata targets are blocked")

        try:
            port = parsed.port
        except ValueError as exc:
            raise TargetPolicyError("invalid target port") from exc
        port = port or (443 if parsed.scheme == "https" else 80)
        if self.allowed_ports and port not in self.allowed_ports:
            raise TargetPolicyError(f"target port {port} is not allowed")

        host_allowed = self._host_allowed(host)
        resolved = self._resolve(host) if self.resolve_dns else []
        if not host_allowed and self.allowed_hosts:
            raise TargetPolicyError(f"target host {host!r} is not in ZYVOR_TARGET_ALLOWLIST")
        if not resolved and self.resolve_dns:
            raise TargetPolicyError(f"target host {host!r} did not resolve")
        for ip in resolved:
            self._validate_ip(ip, host_allowed=host_allowed)

        # Drop fragments so the same endpoint has one stable policy/audit identity.
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.query, ""))

    def validate_redirect(self, source_url: str, destination_url: str) -> str:
        """Validate every redirect destination, not just the initial URL."""
        self.validate_url(source_url)
        return self.validate_url(destination_url)

    def validate_host(self, raw_host: str, port: int = 443) -> str:
        host = raw_host.strip().lower().rstrip(".")
        if not host or any(ch in host for ch in "/?#@"):
            raise TargetPolicyError("invalid hostname")
        # TLS probes use HTTPS semantics even on a non-standard port.
        self.validate_url(f"https://{host}:{port}/")
        return host

    def _host_allowed(self, host: str) -> bool:
        if not self.allowed_hosts:
            return True
        return any(fnmatch.fnmatchcase(host, pattern) for pattern in self.allowed_hosts)

    def _resolve(self, host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
        try:
            literal = ipaddress.ip_address(host.strip("[]"))
            return [literal]
        except ValueError:
            pass
        try:
            infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        except socket.gaierror:
            return []
        result: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
        for info in infos:
            try:
                ip = ipaddress.ip_address(info[4][0])
            except ValueError:
                continue
            if ip not in result:
                result.append(ip)
        return result

    def _validate_ip(
        self, ip: ipaddress.IPv4Address | ipaddress.IPv6Address, *, host_allowed: bool
    ) -> None:
        if ip in _METADATA_IPS:
            raise TargetPolicyError("cloud metadata IPs are blocked")
        if any(ip in network for network in self.allowed_cidrs):
            return
        risky = (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        )
        if risky and not self.allow_private:
            raise TargetPolicyError(f"target resolves to blocked address {ip}")
        if self.allowed_hosts and not host_allowed:
            raise TargetPolicyError("target host is not allowed")


def validate_target_url(url: str) -> str:
    return TargetPolicy.from_env().validate_url(url)


def validate_target_host(host: str, port: int = 443) -> str:
    return TargetPolicy.from_env().validate_host(host, port)
