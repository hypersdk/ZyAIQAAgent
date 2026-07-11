// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import {PresentationReadingPaths} from '../components/PresentationReadingPaths';
import {PresentationPathHead} from '../components/PresentationPathHead';
import {ContinueReadingBanner} from '../components/ContinueReadingBanner';
import {PresentationsCatalog} from '../components/PresentationsCatalog';
import {ProductPage, MarketingHero, PageContent, CTASection, SectionHeader} from '../components/shared';
import {getClientPresentationIndexRows} from '../data/client-presentations';
import {
  getStandardPresentationPdfFilename,
  getStandardPresentationHtmlFilename,
  STANDARD_PRESENTATION_DECKS,
} from '../data/standard-presentations-catalog';
import {PRESENTATION_READING_PATHS} from '../data/presentation-reading-paths';
import {platform} from '../data/platform-stats';

type RoleTag = 'CIO/CTO' | 'Architect' | 'Engineer' | 'Project Manager' | 'Finance';

interface Presentation {
  title: string;
  audience: string;
  filename: string;
  previewFilename?: string;
  category: string;
  roles: RoleTag[];
}

const categoryColors: Record<string, string> = {
  Business: '#ff8f3f',
  Architecture: '#8b5cf6',
  'Cloud Migration': '#10b981',
  Dashboard: '#06b6d4',
  Security: '#ef4444',
  Operations: '#f59e0b',
  'Disaster Recovery': '#ff8f3f',
  Interactive: '#22c55e',
  'Product client decks': '#14b8a6',
};

const standardPresentations: Presentation[] = STANDARD_PRESENTATION_DECKS.filter((d) => !d.isHtml).map((deck) => ({
  title: deck.title,
  audience: deck.audience,
  filename: getStandardPresentationPdfFilename(deck.filename),
  previewFilename: getStandardPresentationHtmlFilename(deck.filename),
  category: deck.category,
  roles: deck.roles as RoleTag[],
}));

const suiteClientDeck: Presentation = {
  title: 'HyperSDK Platform — Complete Suite (Client)',
  audience: `All stakeholders · ${platform.products} products in one storyline`,
  filename: 'client/hypersdk-platform-suite-client-deck.pdf',
  previewFilename: 'client/hypersdk-platform-suite-client-deck.html',
  category: 'Product client decks',
  roles: ['CIO/CTO', 'Architect', 'Engineer', 'Project Manager'],
};

const presentations: Presentation[] = [
  ...standardPresentations,
  suiteClientDeck,
  ...getClientPresentationIndexRows().map((row) => ({
    title: row.title,
    audience: row.audience,
    filename: row.filename,
    previewFilename: row.previewFilename,
    category: 'Product client decks',
    roles: ['CIO/CTO', 'Architect', 'Engineer', 'Project Manager'] as RoleTag[],
  })),
];

const pathIds = PRESENTATION_READING_PATHS.map((p) => p.id);

export default function Presentations(): ReactNode {
  return (
    <ProductPage
      title="Presentations"
      description="HyperSDK Platform slide decks as hyper2kvm-format PDFs — downloadable for client and internal reviews."
    >
      <PresentationPathHead
        allowedPaths={pathIds}
        fallbackTitle="Presentations · Zyvor"
        fallbackDescription="HyperSDK Platform slide decks as hyper2kvm-format PDFs — downloadable for client and internal reviews."
      />
      <MarketingHero
        pageId="presentations"
        description={`${presentations.length} decks in hyper2kvm presentation format (A4 portrait, purple cover, orange accent). Start with a guided path by role — or browse the full catalog below.`}
      />

      <PageContent>
        <ContinueReadingBanner />
        <PresentationReadingPaths contactIntent="demo" />

        <SectionHeader
          eyebrow="Full catalog"
          title="All presentations"
          subtitle="Every synced deck across the suite — filter by product or use the guided paths above."
          spaced
        />

        <PresentationsCatalog presentations={presentations} categoryColors={categoryColors} />

        <CTASection
          title="Need a Custom Presentation?"
          subtitle="We can prepare tailored hyper2kvm-format decks for your migration scenario or product deep dive."
          primaryCta={{label: 'Schedule a Demo', to: '/contact?intent=demo'}}
          secondaryCta={{label: 'Contact Sales', to: '/contact?intent=sales'}}
        />
      </PageContent>
    </ProductPage>
  );
}
