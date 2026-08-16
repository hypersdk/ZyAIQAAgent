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
 * Target environment helpers for Zyvor Argus tests.
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
