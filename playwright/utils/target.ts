/**
 * Target environment helpers for Zyvor QA tests.
 */

export function getTargetUrl(): string {
  return process.env.ZYVOR_STAGING_URL || process.env.ZYVOR_BASE_URL || 'https://zyvor.dev';
}

export function isMarketingSite(): boolean {
  const url = getTargetUrl();
  return url.includes('zyvor.dev') && !process.env.ENABLE_DASHBOARD_TESTS;
}

export function hasAuthCredentials(): boolean {
  if (isMarketingSite()) {
    return false;
  }
  return Boolean(
    getTargetUrl() &&
      process.env.ZYVOR_TEST_USER &&
      process.env.ZYVOR_TEST_PASSWORD
  );
}
