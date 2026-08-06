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

import { defineConfig, devices } from '@playwright/test';
import path from 'path';

const baseURL = process.env.ZYVOR_BASE_URL || 'https://zyvor.dev';
const repoRoot = path.resolve(__dirname, '..');
const playwrightDir = __dirname;
const multiBrowser = process.env.ENABLE_MULTI_BROWSER === 'true';
const regressionMode = process.env.ENABLE_REGRESSION === 'true';
const authSetup =
  process.env.ENABLE_AUTH_SETUP === 'true' &&
  Boolean(process.env.ZYVOR_TEST_USER && process.env.ZYVOR_TEST_PASSWORD) &&
  process.env.ENABLE_DASHBOARD_TESTS === 'true';
const emulation = process.env.ENABLE_EMULATION_PROJECTS === 'true';
const locale = process.env.ZYVOR_LOCALE || 'en-US';
const noSandbox = process.env.ZYVOR_NO_SANDBOX === 'true';

const authFile = path.join(playwrightDir, '.auth', 'user.json');

const sharedUse = {
  baseURL,
  ignoreHTTPSErrors: process.env.ZYVOR_IGNORE_HTTPS_ERRORS === 'true',
  trace: 'retain-on-failure' as const,
  screenshot: (regressionMode ? 'on' : 'only-on-failure') as 'on' | 'only-on-failure',
  video: {
    mode: (process.env.ZYVOR_VIDEO === 'on' ? 'on' : 'retain-on-failure') as 'on' | 'retain-on-failure',
    size: { width: 1280, height: 720 },
  },
  actionTimeout: 15000,
  navigationTimeout: 30000,
  launchOptions: noSandbox ? { args: ['--no-sandbox'] } : {},
  ...(authSetup ? { storageState: authFile } : {}),
};

type Project = NonNullable<Parameters<typeof defineConfig>[0]['projects']>[number];
const projects: Project[] = [];
const browserDeps = authSetup ? ['setup'] : [];

if (authSetup) {
  projects.push({
    name: 'setup',
    testDir: playwrightDir,
    testMatch: /auth\.setup\.ts/,
    use: {
      ...sharedUse,
      storageState: undefined,
    },
  });
}

projects.push({
  name: 'chromium',
  testDir: path.join(repoRoot, 'tests'),
  testMatch: /.*\.spec\.ts/,
  dependencies: browserDeps,
  use: { ...devices['Desktop Chrome'], ...sharedUse },
});

if (multiBrowser) {
  projects.push(
    {
      name: 'firefox',
      testDir: path.join(repoRoot, 'tests'),
      testMatch: /.*\.spec\.ts/,
      dependencies: browserDeps,
      use: { ...devices['Desktop Firefox'], ...sharedUse },
    },
    {
      name: 'webkit',
      testDir: path.join(repoRoot, 'tests'),
      testMatch: /.*\.spec\.ts/,
      dependencies: browserDeps,
      use: { ...devices['Desktop Safari'], ...sharedUse },
    },
  );
}

if (emulation) {
  projects.push(
    {
      name: 'chromium-dark',
      testDir: path.join(repoRoot, 'tests'),
      testMatch: /.*\.spec\.ts/,
      dependencies: browserDeps,
      use: { ...devices['Desktop Chrome'], ...sharedUse, colorScheme: 'dark' as const },
    },
    {
      name: 'chromium-reduced-motion',
      testDir: path.join(repoRoot, 'tests'),
      testMatch: /.*\.spec\.ts/,
      dependencies: browserDeps,
      use: {
        ...devices['Desktop Chrome'],
        ...sharedUse,
        contextOptions: { reducedMotion: 'reduce' as const },
      },
    },
    {
      name: 'chromium-locale',
      testDir: path.join(repoRoot, 'tests'),
      testMatch: /.*\.spec\.ts/,
      dependencies: browserDeps,
      use: { ...devices['Desktop Chrome'], ...sharedUse, locale },
    },
  );
}

export default defineConfig({
  // Projects set their own testDir; keep a root for reporters
  testDir: path.join(repoRoot, 'tests'),
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI
    ? 1
    : process.env.ZYVOR_PW_WORKERS
      ? parseInt(process.env.ZYVOR_PW_WORKERS, 10)
      : undefined,
  reporter: [
    ['list'],
    ['html', { outputFolder: path.join(repoRoot, 'reports'), open: 'never' }],
    ['json', { outputFile: path.join(repoRoot, 'reports', 'results.json') }],
  ],
  use: sharedUse,
  outputDir: path.join(repoRoot, 'test-results'),
  preserveOutput: 'always',
  projects,
});
