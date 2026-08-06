// Copyright 2026 ZyvorAI Labs Private Limited
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * SSRF guardrails for browser-driven crawls of arbitrary, caller-supplied
 * URLs (e.g. a prospective tenant's website submitted at onboarding).
 *
 * Mirrors the intent of orchestrator/security/target_policy.py (same
 * metadata-IP/private-range blocklist), but is enforced in-process before
 * every page.goto() rather than only at the initial URL, since a page can
 * redirect or a hostname can resolve differently between the first check
 * and navigation (DNS rebinding / TOCTOU).
 */

import dns from 'node:dns/promises';
import net from 'node:net';

export class TargetPolicyError extends Error {}

const METADATA_HOSTS = new Set(['metadata.google.internal', 'metadata.google', 'instance-data.ec2.internal']);
const METADATA_IPS = new Set(['169.254.169.254', '169.254.170.2', '100.100.100.200']);

function allowPrivateTargets() {
  return /^(1|true|yes|on)$/i.test(process.env.CRAWL_ALLOW_PRIVATE_TARGETS || '');
}

function ipIsRisky(ip) {
  const type = net.isIP(ip);
  if (!type) return true; // not a literal IP — caller resolved something unparsable, treat as risky
  if (METADATA_IPS.has(ip)) return true;
  if (type === 4) {
    const parts = ip.split('.').map(Number);
    const [a, b] = parts;
    if (a === 10) return true; // 10.0.0.0/8
    if (a === 172 && b >= 16 && b <= 31) return true; // 172.16.0.0/12
    if (a === 192 && b === 168) return true; // 192.168.0.0/16
    if (a === 127) return true; // loopback
    if (a === 169 && b === 254) return true; // link-local
    if (a === 0) return true; // unspecified/reserved
    if (a >= 224) return true; // multicast/reserved
  } else if (type === 6) {
    const lower = ip.toLowerCase();
    if (lower === '::1') return true; // loopback
    if (lower === '::') return true; // unspecified
    if (lower.startsWith('fc') || lower.startsWith('fd')) return true; // unique local (fc00::/7)
    if (lower.startsWith('fe80:')) return true; // link-local
    if (lower.startsWith('ff')) return true; // multicast
  }
  return false;
}

/**
 * Validate a URL is safe to navigate to: http(s) only, no embedded
 * credentials, hostname not a cloud-metadata alias, and every resolved IP
 * outside private/loopback/link-local/multicast/reserved ranges (unless
 * CRAWL_ALLOW_PRIVATE_TARGETS is explicitly set, for local dev targets).
 * Throws TargetPolicyError on any violation.
 */
export async function assertSafeTarget(rawUrl) {
  let parsed;
  try {
    parsed = new URL(rawUrl);
  } catch {
    throw new TargetPolicyError(`invalid target URL: ${rawUrl}`);
  }
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    throw new TargetPolicyError(`target scheme must be http or https: ${rawUrl}`);
  }
  if (parsed.username || parsed.password) {
    throw new TargetPolicyError('credentials must not be embedded in target URLs');
  }
  const host = parsed.hostname.toLowerCase().replace(/\.$/, '');
  if (!host) {
    throw new TargetPolicyError('target hostname is required');
  }
  if (METADATA_HOSTS.has(host) || (host.endsWith('.internal') && host.includes('metadata'))) {
    throw new TargetPolicyError('cloud metadata targets are blocked');
  }

  if (allowPrivateTargets()) return;

  const literal = net.isIP(host);
  const ips = literal ? [host] : await resolveHost(host);
  if (ips.length === 0) {
    throw new TargetPolicyError(`target host did not resolve: ${host}`);
  }
  for (const ip of ips) {
    if (ipIsRisky(ip)) {
      throw new TargetPolicyError(`target resolves to a blocked address: ${ip}`);
    }
  }
}

async function resolveHost(host) {
  try {
    const records = await dns.lookup(host, { all: true, verbatim: true });
    return records.map((r) => r.address);
  } catch {
    return [];
  }
}
