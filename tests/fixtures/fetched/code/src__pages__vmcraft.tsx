// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {Redirect} from '@docusaurus/router';
import {ProductPage} from '../components/shared';

/** Legacy URL — VMCraft engine is part of hyper2kvm. */
export default function VMCraft(): ReactNode {
  return (
    <ProductPage title="VMCraft Engine" description="Redirecting to hyper2kvm.">
      <Redirect to="/hyper2kvm" />
    </ProductPage>
  );
}
