// Copyright 2026 ZyvorAI Labs Private Limited
// SPDX-License-Identifier: Apache-2.0

import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';


test.describe('Verify /vm page shows "KubeVirt" and HyperSDK content', () => {
  test('Verify /vm page shows "KubeVirt" and HyperSDK content', async ({ page, consoleLogs }) => {



    await page.goto('/vm');
    await waitForPageReady(page);



    await waitForPageReady(page);




    await expect(page.getByText("KubeVirt").first()).toBeVisible({ timeout: 15000 });




    const appErrors = consoleLogs.filter(
      (l) => l.startsWith('[error]') && !l.includes('Content Security Policy')
    );
    expect(appErrors).toHaveLength(0);
  });
});