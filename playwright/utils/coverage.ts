import fs from 'fs';
import path from 'path';

export type V8CoverageEntry = {
  url: string;
  scriptId: string;
  source?: string;
  functions: Array<{
    functionName: string;
    ranges: Array<{ startOffset: number; endOffset: number; count: number }>;
    isBlockCoverage: boolean;
  }>;
};

type Range = { startOffset: number; endOffset: number; count: number };

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'test';
}

function rangeBytes(ranges: Range[]): { total: number; used: number } {
  let total = 0;
  let used = 0;
  for (const range of ranges) {
    const size = Math.max(0, range.endOffset - range.startOffset);
    total += size;
    if (range.count > 0) {
      used += size;
    }
  }
  return { total, used };
}

export function summarizeCoverage(entries: V8CoverageEntry[]) {
  let totalBytes = 0;
  let usedBytes = 0;
  const files: Array<{ url: string; total_bytes: number; used_bytes: number; percentage: number }> = [];

  for (const entry of entries) {
    let fileTotal = 0;
    let fileUsed = 0;
    for (const fn of entry.functions) {
      const { total, used } = rangeBytes(fn.ranges as Range[]);
      fileTotal += total;
      fileUsed += used;
    }
    totalBytes += fileTotal;
    usedBytes += fileUsed;
    if (fileTotal > 0) {
      files.push({
        url: entry.url,
        total_bytes: fileTotal,
        used_bytes: fileUsed,
        percentage: Math.round((fileUsed / fileTotal) * 10000) / 100,
      });
    }
  }

  const percentage = totalBytes > 0 ? Math.round((usedBytes / totalBytes) * 10000) / 100 : 0;
  return { total_bytes: totalBytes, used_bytes: usedBytes, percentage, files };
}

export async function writeCoverageArtifact(
  testInfo: { title: string; outputPath: (name: string) => string },
  coverage: V8CoverageEntry[],
  repoRoot: string,
): Promise<void> {
  const summary = summarizeCoverage(coverage);
  const dir = path.join(repoRoot, 'reports', 'v8-coverage');
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${slugify(testInfo.title)}.json`);
  fs.writeFileSync(
    file,
    JSON.stringify({ test_title: testInfo.title, summary, entries: coverage }, null, 2),
  );
  await testInfo.attach('v8-coverage.json', {
    body: JSON.stringify(summary),
    contentType: 'application/json',
  });
}
