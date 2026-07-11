import { test, expect } from '@playwright/test';
import { waitForPageReady } from '../../playwright/utils/helpers';

test.describe('VM Infrastructure — zyvor.dev marketing', () => {
  test('VM migration and infrastructure content is visible', async ({ page }) => {
    await page.goto('/');
    await waitForPageReady(page);

    await expect(page.getByText(/VM|KubeVirt|migration/i).first()).toBeAttached();
    await expect(page.getByText(/HyperSDK|Zeus OS/i).first()).toBeAttached();
    await expect(page.getByText(/96\.8%|first-boot/i).first()).toBeAttached();
  });

  test('/vm route serves marketing site (no dashboard login)', async ({ page }) => {
    await page.goto('/vm');
    await waitForPageReady(page);

    await expect(page).toHaveTitle(/Zyvor|HyperSDK/i);
    await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible();
    await expect(page.getByRole('button', { name: /Create VM/i })).toHaveCount(0);
  });
});
