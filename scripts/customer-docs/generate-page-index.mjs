#!/usr/bin/env node
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

import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const OUT = resolve(ROOT, 'docs/customer/PAGE_INDEX.md')
const GUIDES = resolve(ROOT, 'docs/customer/pages')
const { routes } = JSON.parse(readFileSync(resolve(ROOT, 'scripts/customer-docs/routes.json'), 'utf8'))
const purposes = JSON.parse(readFileSync(resolve(ROOT, 'scripts/customer-docs/page-purposes.json'), 'utf8'))
const PRODUCT = process.env.CUSTOMER_DOCS_PRODUCT || 'Zyvor Argus'

function discoverGuides(dir) {
  const map = new Map()
  if (!existsSync(dir)) return map
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue
    for (const file of readdirSync(join(dir, entry.name))) {
      if (!file.endsWith('.md') || file === 'README.md') continue
      map.set(file.replace(/\.md$/, ''), `pages/${entry.name}/${file}`)
    }
  }
  return map
}

function slug(path) {
  return path.replace(/^\//, '').replace(/\//g, '-').replace(/\?.*/, '') || 'home'
}

const guides = discoverGuides(GUIDES)
const byCat = new Map()
for (const r of routes) {
  if (!byCat.has(r.category)) byCat.set(r.category, [])
  byCat.get(r.category).push(r)
}

const lines = [
  `# ${PRODUCT} — Complete page index`,
  '',
  'Every Mission Control surface and action card.',
  '',
  `_Generated: ${new Date().toISOString().slice(0, 10)} · ${routes.length} routes_`,
  '',
  'Regenerate: `node scripts/customer-docs/generate-page-index.mjs`',
  '',
]

for (const [cat, list] of byCat) {
  lines.push(`## ${cat}`, '', '| Page | Route | Purpose | Guide |', '|------|-------|---------|-------|')
  for (const it of list) {
    const purpose = (purposes[it.path] || '').replace(/\|/g, '\\|')
    const g = guides.get(slug(it.path))
    lines.push(`| ${it.label} | \`${it.path}\` | ${purpose} | ${g ? `[Open](${g})` : '—'} |`)
  }
  lines.push('')
}

lines.push('## Related', '', '- [Customer docs home](README.md)', '- [Page-by-page guides](pages/README.md)', '')
writeFileSync(OUT, lines.join('\n'))
console.log(`Wrote ${OUT}`)
