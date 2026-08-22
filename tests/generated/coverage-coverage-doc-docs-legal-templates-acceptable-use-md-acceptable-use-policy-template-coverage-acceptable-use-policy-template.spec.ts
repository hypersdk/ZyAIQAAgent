// Copyright 2026 ZyvorAI Labs Private Limited
// SPDX-License-Identifier: Apache-2.0

import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';


test.describe('Coverage: Acceptable Use Policy (template)', () => {
  test('Coverage: Acceptable Use Policy (template)', async ({ page, consoleLogs }) => {



    await page.goto('/acceptable-use-policy-template');
    await waitForPageReady(page);



    await waitForPageReady(page);




    await expect(page.getByText(/Acceptable Use Policy (template)/i).first()).toBeVisible({ timeout: 15000 });




    const appErrors = consoleLogs.filter(
      (l) => l.startsWith('[error]') && !l.includes('Content Security Policy')
    );
    expect(appErrors).toHaveLength(0);
  });
});