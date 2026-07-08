import { Page, expect } from '@playwright/test';

/**
 * Wait for page to be fully loaded and interactive.
 */
export async function waitForPageReady(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle').catch(() => {
    // networkidle may timeout on sites with long-polling; non-fatal
  });
}

/**
 * Assert no critical console errors occurred.
 */
export async function assertNoConsoleErrors(consoleLogs: string[]): Promise<void> {
  const errors = consoleLogs.filter((log) => log.startsWith('[error]'));
  expect(errors, `Console errors: ${errors.join(', ')}`).toHaveLength(0);
}
