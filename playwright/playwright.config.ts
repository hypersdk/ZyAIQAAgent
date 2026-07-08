import { defineConfig, devices } from '@playwright/test';
import path from 'path';

const baseURL = process.env.ZYVOR_BASE_URL || 'https://zyvor.dev';
const repoRoot = path.resolve(__dirname, '..');

export default defineConfig({
  testDir: path.join(repoRoot, 'tests'),
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['list'],
    ['html', { outputFolder: path.join(repoRoot, 'reports'), open: 'never' }],
    ['json', { outputFile: path.join(repoRoot, 'reports', 'results.json') }],
  ],
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },
  outputDir: path.join(repoRoot, 'test-results'),
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
