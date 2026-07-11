// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {Redirect} from '@docusaurus/router';
import {ProductPage} from '../components/shared';

/** Legacy product URL — VirtSpawn capabilities live in Machina. */
export default function VirtSpawnLegacy(): ReactNode {
  return (
    <ProductPage title="VirtSpawn" description="Redirecting to Machina.">
      <Redirect to="/machina" />
    </ProductPage>
  );
}
