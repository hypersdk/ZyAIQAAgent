import { test as base, expect } from '@playwright/test';

export type LogFixtures = {
  consoleLogs: string[];
  networkErrors: string[];
};

export const test = base.extend<LogFixtures>({
  consoleLogs: async ({ page }, use) => {
    const logs: string[] = [];
    page.on('console', (msg) => {
      logs.push(`[${msg.type()}] ${msg.text()}`);
    });
    await use(logs);
  },

  networkErrors: async ({ page }, use) => {
    const errors: string[] = [];
    page.on('response', (response) => {
      if (response.status() >= 400) {
        errors.push(`${response.status()} ${response.url()}`);
      }
    });
    await use(errors);
  },
});

export { expect };
