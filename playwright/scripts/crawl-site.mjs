/**
 * BFS crawl of a live site — outputs JSON coverage candidates to stdout.
 *
 * Usage:
 *   node playwright/scripts/crawl-site.mjs [baseUrl] [maxPages] [maxDepth]
 */

import { chromium } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '../..');

const baseUrl = process.argv[2] || process.env.ZYVOR_BASE_URL || 'https://zyvor.dev';
const maxPages = parseInt(process.argv[3] || process.env.CRAWL_MAX_PAGES || '50', 10);
const maxDepth = parseInt(process.argv[4] || process.env.CRAWL_MAX_DEPTH || '2', 10);

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
  const origin = new URL(baseUrl).origin;
  const queue = [{ path: '/', depth: 0 }];
  const visited = new Set();
  const candidates = [];

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  while (queue.length > 0 && visited.size < maxPages) {
    const { path: routePath, depth } = queue.shift();
    if (visited.has(routePath)) continue;
    visited.add(routePath);

    const url = routePath === '/' ? origin + '/' : origin + routePath;
    try {
      const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      const title = (await page.title()) || routePath;
      const status = response?.status() ?? 0;

      candidates.push({
        id: `crawl-${slug(routePath)}`,
        kind: 'route',
        path: routePath,
        title: title.trim() || routePath,
        signals: ['live-crawl', `status:${status}`],
        priority: depth === 0 ? 'high' : 'medium',
        source_file: 'live-crawl',
        context: `Crawled ${url} — HTTP ${status}`,
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
