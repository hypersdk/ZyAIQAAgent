import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';
import { validateApiCalls } from '../../playwright/utils/api';

test.describe('Zyvor Product Suite', () => {
  test('product suite section is visible on homepage', async ({ page, apiCalls }) => {
    await page.goto('/');
    await waitForPageReady(page);

    await expect(
      page.getByRole('heading', { name: /14.*products|product suite|HyperSDK/i }).first()
    ).toBeVisible({ timeout: 15000 });

    const apiFailures = validateApiCalls(apiCalls, [
      { urlPattern: /zyvor\.dev/, method: 'GET', expectedStatus: 200 },
    ]);
    expect(apiFailures).toHaveLength(0);
  });

  test('key product names are present in page content', async ({ page }) => {
    await page.goto('/');
    await waitForPageReady(page);

    const products = ['HyperSDK', 'hyper2kvm', 'Zeus OS', 'PacketWolf', 'Aether'];

    for (const product of products) {
      await expect(page.getByText(product, { exact: false }).first()).toBeAttached();
    }
  });

  test('migration providers are mentioned in page content', async ({ page }) => {
    await page.goto('/');
    await waitForPageReady(page);

    const providers = page.getByText(/VMware|OpenStack|KubeVirt/i);
    await expect(providers.first()).toBeAttached();
    expect(await providers.count()).toBeGreaterThan(0);
  });
});
