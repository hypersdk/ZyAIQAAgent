import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';

test.describe('Zyvor Homepage', () => {
  test('homepage loads with hero content visible', async ({ page, consoleLogs }) => {
    await page.goto('/');
    await waitForPageReady(page);

    await expect(page).toHaveTitle(/Zyvor|HyperSDK/i);
    await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible();
    const appErrors = consoleLogs.filter(
      (l) => l.startsWith('[error]') && !l.includes('Content Security Policy')
    );
    expect(appErrors).toHaveLength(0);
  });

  test('main navigation is accessible', async ({ page }) => {
    await page.goto('/');
    await waitForPageReady(page);

    const nav = page.getByRole('navigation').first();
    await expect(nav).toBeVisible();
  });

  test('page has no critical accessibility landmarks', async ({ page }) => {
    await page.goto('/');
    await waitForPageReady(page);

    await expect(page.locator('body')).toBeVisible();
    const links = page.getByRole('link');
    expect(await links.count()).toBeGreaterThan(0);
  });
});
