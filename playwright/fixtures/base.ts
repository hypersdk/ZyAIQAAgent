import { test as base, expect } from '@playwright/test';

export type LogFixtures = {
  consoleLogs: string[];
  networkErrors: string[];
  apiCalls: { url: string; method: string; status: number }[];
};

export const test = base.extend<LogFixtures>({
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
