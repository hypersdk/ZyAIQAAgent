import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';
import { captureBaseline } from '../../playwright/utils/api';

test.describe('Visual Regression', () => {
  test('homepage visual baseline', async ({ page }) => {
    await page.goto('/');
    await waitForPageReady(page);

    await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible();

    if (process.env.ENABLE_REGRESSION === 'true') {
      await captureBaseline(page, 'homepage-hero');
    }
  });

  test('products section visual baseline', async ({ page }) => {
    await page.goto('/');
    await waitForPageReady(page);

    const section = page.getByText(/14.*products|All 14|product suite/i).first();
    await section.scrollIntoViewIfNeeded();
    await expect(section).toBeAttached();

    if (process.env.ENABLE_REGRESSION === 'true') {
      await captureBaseline(page, 'products-section');
    }
  });
});
