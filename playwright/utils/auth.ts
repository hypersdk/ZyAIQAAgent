import { Page } from '@playwright/test';
import { getTargetUrl, hasAuthCredentials, isMarketingSite } from './target';

export { getTargetUrl, hasAuthCredentials, isMarketingSite };

/** @deprecated Use hasAuthCredentials */
export function hasStagingCredentials(): boolean {
  return hasAuthCredentials();
}

/**
 * Authenticate against a Zyvor dashboard (not available on the public marketing site).
 */
export async function login(page: Page): Promise<void> {
  if (isMarketingSite()) {
    throw new Error(
      'Login is not available on zyvor.dev (marketing site). ' +
        'Set ENABLE_DASHBOARD_TESTS=true and a dashboard URL to run auth tests.'
    );
  }

  const targetUrl = getTargetUrl();
  const user = process.env.ZYVOR_TEST_USER;
  const password = process.env.ZYVOR_TEST_PASSWORD;

  if (!user || !password) {
    throw new Error(
      'Login requires ZYVOR_TEST_USER and ZYVOR_TEST_PASSWORD in .env'
    );
  }

  await page.goto(targetUrl);
  await page.getByLabel(/email|username/i).fill(user);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /sign in|log in/i }).click();
  await page.waitForURL(/dashboard|home|vm/i, { timeout: 30000 });
}
