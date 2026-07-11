---
title: Proprietary software policy
description: Zyvor proprietary distribution policy and how third-party open-source dependencies are handled in builds.
sidebar_label: Proprietary policy
---

# Proprietary software policy

## Position

ZyvorAI Labs does **not** distribute proprietary suite products under Apache 2.0, MIT, or similar open-source licenses. This applies to **PacketWolf**, **Ragnarok**, **Aether**, **HyperSDK Platform**, **Forge**, **IronWolf**, **HyperCluster**, **Zeus OS**, **Zyvor Fabric**, **Veyron**, **Machina**, **hyper2kvm**, and related commercial extensions.

**GuestKit** is the exception: guest inspection source is **LGPL-3.0-or-later**. Zyvor-branded GuestKit binaries and enterprise bundles remain subject to company acceptance terms in addition to LGPL obligations.

## Third-party dependencies

Compiled products may **link to** third-party open-source libraries (e.g., crates, system libraries). Those components remain governed by their respective licenses. A **NOTICE** file (where provided) lists third-party attributions. That does **not**:

- Grant rights to Zyvor’s proprietary source or binaries
- Permit redistribution of Zyvor products without a written license
- Grant trademark rights

## Customer agreements

Agreements should state:

> All Zyvor product software, documentation, and commercial extensions are proprietary to ZyvorAI Labs Private Limited. Third-party components embedded in builds remain subject only to their own licenses.

## Repositories

- Do not add `LICENSE` files implying Apache/MIT for Zyvor-owned code.
- Use the company **proprietary LICENSE** (synced via `scripts/sync-proprietary-license.sh`).
- Keep confidential materials out of public repos; if a repo is private, access is still under proprietary terms unless a separate contract says otherwise.

## Contributions

If external contributors are accepted, use a written **CLA** or assignment—counsel to draft. No public OSS release without board approval.
