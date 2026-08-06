// Copyright 2026 ZyvorAI Labs Private Limited
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * Playwright setup project — login once and write storageState for dependent projects.
 * Enabled when ENABLE_AUTH_SETUP=true and credentials are present.
 */
import { test as setup, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { login, hasAuthCredentials } from './utils/auth';

const AUTH_DIR = path.join(__dirname, '.auth');
const AUTH_FILE = path.join(AUTH_DIR, 'user.json');

setup('authenticate', async ({ page }) => {
  setup.skip(!hasAuthCredentials(), 'No dashboard credentials — skip auth setup');

  fs.mkdirSync(AUTH_DIR, { recursive: true });
  await login(page);
  await expect(page).toHaveURL(/dashboard|home|vm/i, { timeout: 30000 });

  // Capture cookies + localStorage (Playwright), then enrich with sessionStorage + token
  const state = await page.context().storageState();
  const sessionStorageData = await page.evaluate(() => {
    const out: Record<string, string> = {};
    for (let i = 0; i < sessionStorage.length; i++) {
      const k = sessionStorage.key(i);
      if (k) out[k] = sessionStorage.getItem(k) || '';
    }
    return out;
  });
  const token =
    sessionStorageData['token'] ||
    sessionStorageData['access_token'] ||
    sessionStorageData['auth_token'] ||
    sessionStorageData['jwt'] ||
    '';

  const enriched = {
    ...state,
    _sessionStorage: JSON.stringify(sessionStorageData),
    _token: token,
  };
  fs.writeFileSync(AUTH_FILE, JSON.stringify(enriched, null, 2));
});
