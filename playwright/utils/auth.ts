import { Page } from '@playwright/test';

/**
 * Authenticate against Zyvor staging (requires ZYVOR_STAGING_URL + credentials).
 */
export async function login(page: Page): Promise<void> {
  const stagingUrl = process.env.ZYVOR_STAGING_URL;
  const user = process.env.ZYVOR_TEST_USER;
  const password = process.env.ZYVOR_TEST_PASSWORD;

  if (!stagingUrl || !user || !password) {
    throw new Error(
      'Login requires ZYVOR_STAGING_URL, ZYVOR_TEST_USER, and ZYVOR_TEST_PASSWORD'
    );
  }

  await page.goto(stagingUrl);
  await page.getByLabel(/email|username/i).fill(user);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /sign in|log in/i }).click();
  await page.waitForURL(/dashboard|home/i);
}
