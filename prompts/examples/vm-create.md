# Administrator creates a VM — marketing site validation

**As a** visitor
**I want to** see VM and infrastructure capabilities on zyvor.dev
**So that** I can evaluate the Zyvor platform

## Acceptance Criteria

1. Homepage loads at `https://zyvor.dev`
2. VM migration and KubeVirt content is visible
3. HyperSDK / Zeus OS product names are listed
4. `/vm` route serves the marketing site (no dashboard login)

## Environment

- Target: `ZYVOR_BASE_URL=https://zyvor.dev` (marketing site only)
- No dashboard or staging environment required

## Tags

vm, marketing, smoke
