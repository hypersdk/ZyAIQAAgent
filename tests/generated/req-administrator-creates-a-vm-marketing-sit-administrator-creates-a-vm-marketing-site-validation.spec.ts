// Copyright 2026 ZyvorAI Labs Private Limited
// SPDX-License-Identifier: Apache-2.0

import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';


test.describe('Administrator creates a VM — marketing site validation', () => {
  test('Administrator creates a VM — marketing site validation', async ({ page, consoleLogs }) => {



    await page.goto('/');
    await waitForPageReady(page);



    await page.goto('/vm');
    await waitForPageReady(page);



    const appErrors = consoleLogs.filter(
      (l) => l.startsWith('[error]') && !l.includes('Content Security Policy')
    );
    expect(appErrors).toHaveLength(0);
  });
});