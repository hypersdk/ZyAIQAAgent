// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {ProductPage, PageContent, CTASection} from '../../components/shared';
import {GuidedDecksHub} from '../../components/GuidedDecksHub';

export default function DecksIndex(): ReactNode {
  return (
    <ProductPage
      title="Guided deck paths"
      description="Curated Zyvor client presentation paths by role — CIO, architect, program manager, VMware exit, and confidential computing."
    >
      <PageContent>
        <GuidedDecksHub hideHeader />
        <CTASection
          title="Need a custom deck?"
          subtitle="We prepare tailored hyper2kvm-format presentations for your migration scenario."
          primaryCta={{label: 'Schedule a demo', to: '/contact?intent=demo'}}
          secondaryCta={{label: 'VMware exit program', to: '/vmware-exit?path=vmware-exit'}}
        />
      </PageContent>
    </ProductPage>
  );
}
