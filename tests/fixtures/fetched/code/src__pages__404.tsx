// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import {ProductPage, MarketingHero, PageContent, styles} from '../components/shared';

export default function NotFound(): ReactNode {
  return (
    <ProductPage title="Page Not Found" description="The page you're looking for doesn't exist or has been moved.">
      <MarketingHero pageId="404" />

      <PageContent>
        <div className={styles.autoFillGrid} style={{maxWidth: 720, margin: '0 auto 3rem'}}>
          {[
            {label: 'Suite hub', to: '/docs/products', desc: 'All twelve products and specs'},
            {label: 'Confidential computing', to: '/confidential-computing', desc: 'SEV-SNP/TDX on KubeVirt'},
            {label: 'OpenStack', to: '/docs/openstack', desc: 'Nova, Glance, and private cloud'},
            {label: 'Presentations', to: '/presentations', desc: 'Download client PDF decks'},
            {label: 'Solutions', to: '/solutions', desc: 'VMware exit, DR, multi-cloud'},
            {label: 'Documentation', to: '/docs/intro', desc: 'Platform docs and quickstart'},
            {label: 'Pricing', to: '/pricing', desc: 'Plans and enterprise options'},
            {label: 'Schedule demo', to: '/contact?intent=demo', desc: 'Talk to solutions engineering'},
          ].map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={styles.featureCard}
              style={{textDecoration: 'none', display: 'block', padding: '1.25rem 1.5rem'}}
            >
              <h3 className={styles.featureCardTitle} style={{marginBottom: '0.35rem'}}>
                {link.label}
              </h3>
              <p className={styles.featureCardDesc} style={{margin: 0}}>
                {link.desc}
              </p>
            </Link>
          ))}
        </div>
      </PageContent>
    </ProductPage>
  );
}
