import { test as base, expect } from '@playwright/test';
import path from 'path';
import { writeCoverageArtifact } from '../utils/coverage';

export type LogFixtures = {
  consoleLogs: string[];
  networkErrors: string[];
  apiCalls: { url: string; method: string; status: number }[];
};

const repoRoot = path.resolve(__dirname, '../..');
const v8Enabled = () => process.env.ENABLE_V8_COVERAGE === 'true';

export const test = base.extend<LogFixtures>({
  page: async ({ page }, use, testInfo) => {
    if (v8Enabled()) {
      await page.coverage.startJSCoverage();
    }
    await use(page);
    if (v8Enabled()) {
      const coverage = await page.coverage.stopJSCoverage();
      await writeCoverageArtifact(testInfo, coverage, repoRoot);
    }
  },

  consoleLogs: async ({ page }, use, testInfo) => {
    const logs: string[] = [];
    page.on('console', (msg) => {
      logs.push(`[${msg.type()}] ${msg.text()}`);
    });
    await use(logs);
    const logPath = testInfo.outputPath('console.log');
    await testInfo.attach('console.log', {
      body: logs.join('\n'),
      contentType: 'text/plain',
    });
  },

  networkErrors: async ({ page }, use, testInfo) => {
    const errors: string[] = [];
    page.on('response', (response) => {
      if (response.status() >= 400) {
        errors.push(`${response.status()} ${response.request().method()} ${response.url()}`);
      }
    });
    await use(errors);
    if (errors.length > 0) {
      await testInfo.attach('network-errors.log', {
        body: errors.join('\n'),
        contentType: 'text/plain',
      });
    }
  },

  apiCalls: async ({ page }, use) => {
    const calls: { url: string; method: string; status: number }[] = [];
    page.on('response', (response) => {
      calls.push({
        url: response.url(),
        method: response.request().method(),
        status: response.status(),
      });
    });
    await use(calls);
  },
});

export { expect };
