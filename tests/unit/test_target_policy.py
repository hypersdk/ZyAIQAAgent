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

import ipaddress

import pytest

from orchestrator.security.target_policy import TargetPolicy, TargetPolicyError


def test_blocks_metadata_ip():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError):
        policy._validate_ip(ipaddress.ip_address("169.254.169.254"), host_allowed=True)


def test_blocks_private_by_default():
    policy = TargetPolicy(allow_private=False, resolve_dns=False)
    with pytest.raises(TargetPolicyError):
        policy._validate_ip(ipaddress.ip_address("127.0.0.1"), host_allowed=True)


def test_host_allowlist():
    policy = TargetPolicy(allowed_hosts=("*.zyvor.dev", "zyvor.dev"), resolve_dns=False)
    assert policy.validate_url("https://qa.zyvor.dev/path#fragment") == "https://qa.zyvor.dev/path"
    with pytest.raises(TargetPolicyError):
        policy.validate_url("https://example.org/")


def test_userinfo_is_rejected():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError):
        policy.validate_url("https://user:pass@example.org/")


def test_custom_tls_port_uses_https_policy():
    policy = TargetPolicy(allowed_ports=(24631,), allow_http=False, resolve_dns=False)
    assert policy.validate_host("forge.zyvor.dev", 24631) == "forge.zyvor.dev"


# -- from_env ----------------------------------------------------------------


def test_from_env_parses_allowed_cidrs(monkeypatch):
    monkeypatch.setenv("ZYVOR_TARGET_ALLOWED_CIDRS", "10.0.0.0/8, 192.168.0.0/16")
    policy = TargetPolicy.from_env()
    assert len(policy.allowed_cidrs) == 2
    assert ipaddress.ip_network("10.0.0.0/8") in policy.allowed_cidrs


# -- validate_url: basic input validation ------------------------------------


def test_rejects_empty_url():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError, match="is required"):
        policy.validate_url("")


def test_rejects_non_string_url():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError, match="is required"):
        policy.validate_url(None)  # type: ignore[arg-type]


def test_rejects_overlong_url():
    policy = TargetPolicy(resolve_dns=False, max_url_length=20)
    with pytest.raises(TargetPolicyError, match="too long"):
        policy.validate_url("https://example.org/" + "x" * 20)


def test_rejects_non_http_scheme():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError, match="http or https"):
        policy.validate_url("ftp://example.org/")


def test_rejects_http_when_disabled():
    policy = TargetPolicy(resolve_dns=False, allow_http=False)
    with pytest.raises(TargetPolicyError, match="plain HTTP"):
        policy.validate_url("http://example.org/")


def test_rejects_missing_hostname():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError, match="hostname is required"):
        policy.validate_url("https:///path")


def test_blocks_known_metadata_hostname():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError, match="cloud metadata targets"):
        policy.validate_url("https://metadata.google.internal/")


def test_blocks_metadata_shaped_internal_hostname():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError, match="cloud metadata targets"):
        policy.validate_url("https://custom-metadata.internal/")


def test_rejects_out_of_range_port():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError, match="invalid target port"):
        policy.validate_url("https://example.org:99999/")


def test_rejects_disallowed_port():
    policy = TargetPolicy(resolve_dns=False, allowed_ports=(8080,))
    with pytest.raises(TargetPolicyError, match="is not allowed"):
        policy.validate_url("https://example.org/")


def test_validate_url_resolves_literal_ip_and_validates_it():
    policy = TargetPolicy(resolve_dns=True)
    assert policy.validate_url("https://93.184.216.34/") == "https://93.184.216.34/"


def test_validate_url_rejects_resolved_private_ip(monkeypatch):
    from orchestrator.security import target_policy as tp_module

    def fake_getaddrinfo(host, port, **kwargs):
        return [(2, 1, 6, "", ("10.0.0.5", 0))]

    monkeypatch.setattr(tp_module.socket, "getaddrinfo", fake_getaddrinfo)
    policy = TargetPolicy(resolve_dns=True, allow_private=False)
    with pytest.raises(TargetPolicyError, match="blocked address"):
        policy.validate_url("https://internal.example.org/")


def test_resolve_returns_literal_ip_directly():
    policy = TargetPolicy(resolve_dns=True)
    assert policy._resolve("93.184.216.34") == [ipaddress.ip_address("93.184.216.34")]


def test_rejects_unresolvable_host(monkeypatch):
    import socket as real_socket

    from orchestrator.security import target_policy as tp_module

    def fake_getaddrinfo(host, port, **kwargs):
        raise real_socket.gaierror("nope")

    monkeypatch.setattr(tp_module.socket, "getaddrinfo", fake_getaddrinfo)
    policy = TargetPolicy(resolve_dns=True)
    with pytest.raises(TargetPolicyError, match="did not resolve"):
        policy.validate_url("https://does-not-resolve.invalid/")


# -- validate_redirect / validate_host ---------------------------------------


def test_validate_redirect_checks_both_urls():
    policy = TargetPolicy(resolve_dns=False)
    assert policy.validate_redirect(
        "https://example.org/start", "https://example.org/end"
    ) == "https://example.org/end"
    with pytest.raises(TargetPolicyError):
        policy.validate_redirect("https://example.org/start", "ftp://example.org/end")


def test_validate_host_rejects_invalid_characters():
    policy = TargetPolicy(resolve_dns=False)
    with pytest.raises(TargetPolicyError, match="invalid hostname"):
        policy.validate_host("example.org/evil")


# -- _resolve -----------------------------------------------------------------


def test_resolve_skips_unparseable_addresses(monkeypatch):
    from orchestrator.security import target_policy as tp_module

    def fake_getaddrinfo(host, port, **kwargs):
        return [
            (2, 1, 6, "", ("not-an-ip", 0)),
            (2, 1, 6, "", ("93.184.216.34", 0)),
        ]

    monkeypatch.setattr(tp_module.socket, "getaddrinfo", fake_getaddrinfo)
    policy = TargetPolicy(resolve_dns=True)
    resolved = policy._resolve("example.org")
    assert resolved == [ipaddress.ip_address("93.184.216.34")]


# -- _validate_ip: allowed CIDRs and host-allowlist interaction --------------


def test_validate_ip_allowed_via_cidr_bypasses_private_check():
    policy = TargetPolicy(
        allowed_cidrs=(ipaddress.ip_network("10.0.0.0/8"),), allow_private=False
    )
    # would normally be blocked as a private address, but the explicit CIDR wins
    policy._validate_ip(ipaddress.ip_address("10.1.2.3"), host_allowed=True)


def test_validate_ip_rejects_public_ip_not_in_host_allowlist():
    policy = TargetPolicy(allowed_hosts=("example.org",))
    with pytest.raises(TargetPolicyError, match="target host is not allowed"):
        policy._validate_ip(ipaddress.ip_address("93.184.216.34"), host_allowed=False)


# -- module-level convenience wrappers ---------------------------------------


def test_validate_target_url_wrapper(monkeypatch):
    monkeypatch.setenv("ZYVOR_SKIP_TARGET_DNS_RESOLUTION", "true")
    monkeypatch.setenv("ZYVOR_ALLOW_PRIVATE_TARGETS", "true")
    from orchestrator.security.target_policy import validate_target_url

    assert validate_target_url("https://example.org/x") == "https://example.org/x"


def test_validate_target_host_wrapper(monkeypatch):
    monkeypatch.setenv("ZYVOR_SKIP_TARGET_DNS_RESOLUTION", "true")
    monkeypatch.setenv("ZYVOR_ALLOW_PRIVATE_TARGETS", "true")
    from orchestrator.security.target_policy import validate_target_host

    assert validate_target_host("example.org", 443) == "example.org"
