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
 * BFS crawl of a live site — outputs JSON coverage candidates to stdout.
 *
 * Usage:
 *   node playwright/scripts/crawl-site.mjs [baseUrl] [maxPages] [maxDepth]
 */

import { chromium } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { assertSafeTarget } from './lib/target-policy.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '../..');

const baseUrl = process.argv[2] || process.env.ZYVOR_BASE_URL || 'https://zyvor.dev';
const maxPages = parseInt(process.argv[3] || process.env.CRAWL_MAX_PAGES || '50', 10);
const maxDepth = parseInt(process.argv[4] || process.env.CRAWL_MAX_DEPTH || '2', 10);
// Cap on captured page text so a huge page can't blow up memory/output size
// or downstream embedding cost; enough for typical docs/marketing pages.
const maxContentChars = parseInt(process.env.CRAWL_MAX_CONTENT_CHARS || '200000', 10);

function normalizeUrl(href, origin) {
  try {
    const url = new URL(href, origin);
    if (url.origin !== origin) return null;
    url.hash = '';
    const normalized = url.pathname.replace(/\/+$/, '') || '/';
    return normalized;
  } catch {
    return null;
  }
}

function slug(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'page';
}

async function crawl() {
  await assertSafeTarget(baseUrl);
  const origin = new URL(baseUrl).origin;
  const queue = [{ path: '/', depth: 0 }];
  const visited = new Set();
  const candidates = [];

  const browser = await chromium.launch({
    headless: true,
    args: process.env.ZYVOR_NO_SANDBOX === 'true' ? ['--no-sandbox'] : [],
  });
  const context = await browser.newContext({
    ignoreHTTPSErrors: process.env.ZYVOR_IGNORE_HTTPS_ERRORS === 'true',
  });
  const page = await context.newPage();

  // Best-effort login when target credentials are provided, so the crawl can
  // reach authenticated pages. Non-fatal: unknown login forms are skipped.
  const user = process.env.ZYVOR_TEST_USER;
  const password = process.env.ZYVOR_TEST_PASSWORD;
  if (user && password) {
    try {
      await assertSafeTarget(baseUrl);
      await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
      const userField = page
        .locator('input[type="email"], input[name*="user" i], input[name*="email" i], input[type="text"]')
        .first();
      const passField = page.locator('input[type="password"]').first();
      if ((await passField.count()) > 0) {
        await userField.fill(user, { timeout: 5000 });
        await passField.fill(password, { timeout: 5000 });
        await Promise.all([
          page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {}),
          page
            .locator('button[type="submit"], input[type="submit"], button:has-text("sign in"), button:has-text("log in")')
            .first()
            .click({ timeout: 5000 }),
        ]);
        console.error(`crawl: attempted login as ${user}`);
      }
    } catch (err) {
      console.error(`crawl: login attempt skipped (${err})`);
    }
  }

  while (queue.length > 0 && visited.size < maxPages) {
    const { path: routePath, depth } = queue.shift();
    if (visited.has(routePath)) continue;
    visited.add(routePath);

    const url = routePath === '/' ? origin + '/' : origin + routePath;
    try {
      // Re-validated per page, not just at start: a redirect or a hostname
      // that resolves differently between the initial check and navigation
      // (DNS rebinding) must not bypass the SSRF guardrail.
      await assertSafeTarget(url);
      const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      const title = (await page.title()) || routePath;
      const status = response?.status() ?? 0;
      const content = await page
        .evaluate(() => document.body?.innerText || '')
        .catch(() => '');

      candidates.push({
        id: `crawl-${slug(routePath)}`,
        kind: 'route',
        path: routePath,
        title: title.trim() || routePath,
        signals: ['live-crawl', `status:${status}`],
        priority: depth === 0 ? 'high' : 'medium',
        source_file: 'live-crawl',
        context: `Crawled ${url} — HTTP ${status}`,
        content: content.slice(0, maxContentChars).trim(),
      });

      if (depth >= maxDepth) continue;

      const hrefs = await page.$$eval('a[href]', (anchors) =>
        anchors.map((a) => a.getAttribute('href')).filter(Boolean),
      );

      for (const href of hrefs) {
        const normalized = normalizeUrl(href, origin);
        if (normalized && !visited.has(normalized)) {
          queue.push({ path: normalized, depth: depth + 1 });
        }
      }
    } catch (err) {
      candidates.push({
        id: `crawl-${slug(routePath)}-error`,
        kind: 'route',
        path: routePath,
        title: routePath,
        signals: ['live-crawl', 'error'],
        priority: 'low',
        source_file: 'live-crawl',
        context: String(err),
      });
    }
  }

  await browser.close();

  const outputPath = path.join(repoRoot, 'reports', 'crawl-inventory.json');
  const fs = await import('fs');
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(candidates, null, 2));

  process.stdout.write(JSON.stringify(candidates));
}

crawl().catch((err) => {
  console.error(err);
  process.exit(1);
});
