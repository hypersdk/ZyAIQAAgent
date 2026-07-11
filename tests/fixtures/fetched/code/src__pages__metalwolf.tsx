// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {Redirect} from '@docusaurus/router';
import {ProductPage} from '../components/shared';

/** Legacy URL — MetalWolf was renamed to IronWolf. */
export default function MetalWolfLegacy(): ReactNode {
  return (
    <ProductPage title="MetalWolf" description="Redirecting to IronWolf.">
      <Redirect to="/ironwolf" />
    </ProductPage>
  );
}
