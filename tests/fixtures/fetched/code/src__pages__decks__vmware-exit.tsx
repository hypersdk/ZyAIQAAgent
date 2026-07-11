// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {Redirect} from '@docusaurus/router';
import {ProductPage} from '../../components/shared';

export default function DecksVmwareExit(): ReactNode {
  return (
    <ProductPage title="VMware exit decks" description="Redirecting to VMware exit reading path.">
      <Redirect to="/vmware-exit?path=vmware-exit" />
    </ProductPage>
  );
}
