// Copyright 2026 ZyvorAI Labs Private Limited
// SPDX-License-Identifier: Apache-2.0

import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';


test.describe('Coverage: Allow management access only from admin VLAN', () => {
  test('Coverage: Allow management access only from admin VLAN', async ({ page, consoleLogs }) => {



    await page.goto('/allow-management-access-only-from-admin-vlan');
    await waitForPageReady(page);



    await waitForPageReady(page);




    await expect(page.getByText(/Allow management access only from admin VLAN/i).first()).toBeVisible({ timeout: 15000 });




    const appErrors = consoleLogs.filter(
      (l) => l.startsWith('[error]') && !l.includes('Content Security Policy')
    );
    expect(appErrors).toHaveLength(0);
  });
});