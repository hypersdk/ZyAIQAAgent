import { Page } from '@playwright/test';

export interface ApiExpectation {
  urlPattern: string | RegExp;
  method?: string;
  expectedStatus?: number;
}

/**
 * Validate API responses captured during the test.
 */
export function validateApiCalls(
  apiCalls: { url: string; method: string; status: number }[],
  expectations: ApiExpectation[]
): string[] {
  const failures: string[] = [];

  for (const exp of expectations) {
    const pattern = typeof exp.urlPattern === 'string'
      ? new RegExp(exp.urlPattern)
      : exp.urlPattern;
    const method = exp.method ?? 'GET';
    const expectedStatus = exp.expectedStatus ?? 200;

    const match = apiCalls.find(
      (c) => pattern.test(c.url) && c.method === method
    );

    if (!match) {
      failures.push(`No ${method} request matching ${pattern}`);
      continue;
    }
    if (match.status !== expectedStatus) {
      failures.push(
        `${method} ${match.url}: expected ${expectedStatus}, got ${match.status}`
      );
    }
  }

  return failures;
}

/**
 * Assert page loaded without critical console errors.
 */
export function assertNoConsoleErrors(consoleLogs: string[]): void {
  const errors = consoleLogs.filter((l) => l.startsWith('[error]'));
  if (errors.length > 0) {
    throw new Error(`Console errors detected:\n${errors.join('\n')}`);
  }
}

/**
 * Capture a visual baseline screenshot for regression testing.
 */
export async function captureBaseline(
  page: Page,
  name: string,
  baselineDir = 'screenshots/baselines'
): Promise<void> {
  const path = `${baselineDir}/${name}.png`;
  await page.screenshot({ path, fullPage: true });
}
