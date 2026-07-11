// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import {useState, type ReactNode} from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import {PageContent, PageHero, StatGrid, SectionHeader} from '../components/shared';
import {PRODUCT_THEMES, type ProductThemeId} from '../data/product-themes';
import {getProductConcept} from '../data/suite-product-concepts';
import {platform} from '../data/platform-stats';

/** Marketing product index — lifecycle-grouped, themed card grid for the whole suite. */
type ProductCategory = {eyebrow: string; title: string; subtitle: string; ids: ProductThemeId[]};

const CATEGORIES: ProductCategory[] = [
  {
    eyebrow: 'Migrate',
    title: 'Migration & Export',
    subtitle: 'Get workloads off VMware, Nutanix, and public cloud — discover, export, convert, and assure.',
    ids: ['hypersdk', 'hyper2kvm', 'guestkit'],
  },
  {
    eyebrow: 'Run',
    title: 'Kubernetes & VM Management',
    subtitle: 'Operate VMs and applications on Kubernetes, KubeVirt, and libvirt from one control plane.',
    ids: ['zeus-os', 'hermes', 'veyron', 'ragnarok', 'machina', 'zyvor-fabric'],
  },
  {
    eyebrow: 'Operate',
    title: 'Infrastructure',
    subtitle: 'Deploy anywhere, control shared storage, see every packet, schedule GPUs, and automate bare metal.',
    ids: ['aether', 'atlas', 'packetwolf', 'forge', 'ironwolf'],
  },
  {
    eyebrow: 'Scale',
    title: 'Cluster & Compliance',
    subtitle: 'Stand up clusters and sign regulated documents — the bookends of the platform.',
    ids: ['hypercluster', 'zysign'],
  },
];

function ProductCard({id}: {id: ProductThemeId}): ReactNode {
  const theme = PRODUCT_THEMES[id];
  const concept = getProductConcept(id);
  return (
    <Link
      to={theme.path}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.6rem',
        padding: '1.4rem 1.5rem',
        borderRadius: 12,
        background: 'rgba(255,255,255,0.02)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderLeft: `3px solid ${theme.accent}`,
        textDecoration: 'none',
        height: '100%',
        transition: 'background 0.18s ease, border-color 0.18s ease',
      }}
    >
      <div style={{display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: '0.75rem'}}>
        <span style={{fontSize: '1.15rem', fontWeight: 800, color: 'var(--hs-text-white)'}}>{theme.label}</span>
        <span
          style={{
            fontSize: '0.68rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            color: theme.accent,
            whiteSpace: 'nowrap',
          }}
        >
          {theme.suitePhase}
        </span>
      </div>
      <p style={{fontSize: '0.92rem', color: 'var(--hs-text-muted)', lineHeight: 1.55, margin: 0, flexGrow: 1}}>
        {concept.tagline}
      </p>
      <span style={{fontSize: '0.85rem', fontWeight: 600, color: theme.accent}}>Explore {theme.label} →</span>
    </Link>
  );
}

/** Goal → recommended products. Covers all 15 suite products across 7 goals. */
const FINDER_GOALS: {q: string; ids: ProductThemeId[]}[] = [
  {q: 'Leave VMware / migrate to KVM', ids: ['hypersdk', 'hyper2kvm', 'guestkit']},
  {q: 'Run & operate VMs on Kubernetes', ids: ['zeus-os', 'veyron', 'ragnarok', 'hermes']},
  {q: 'Manage bare-metal & libvirt hosts', ids: ['machina', 'zyvor-fabric', 'ironwolf']},
  {q: 'Provision & manage shared storage', ids: ['atlas']},
  {q: 'Observe & secure cluster networking', ids: ['packetwolf']},
  {q: 'Run GPU / AI infrastructure', ids: ['forge']},
  {q: 'Deploy anywhere & stand up clusters', ids: ['aether', 'hypercluster']},
];

function ProductFinder(): ReactNode {
  const [active, setActive] = useState<number | null>(null);
  const goal = active === null ? null : FINDER_GOALS[active];
  return (
    <div
      style={{
        marginTop: '1rem',
        padding: '1.75rem',
        borderRadius: 16,
        background: 'linear-gradient(135deg, rgba(240,88,58,0.06), rgba(255,143,63,0.02))',
        border: '1px solid rgba(240,88,58,0.22)',
      }}
    >
      <SectionHeader
        eyebrow="Find your starting point"
        title="Not sure which products you need?"
        subtitle="Pick a goal — we'll point you to the right tools in the suite."
      />
      <div style={{display: 'flex', flexWrap: 'wrap', gap: '0.6rem', justifyContent: 'center', marginTop: '0.25rem'}}>
        {FINDER_GOALS.map((g, i) => {
          const on = active === i;
          return (
            <button
              key={g.q}
              type="button"
              onClick={() => setActive(on ? null : i)}
              aria-pressed={on}
              style={{
                cursor: 'pointer',
                padding: '0.6rem 1.1rem',
                borderRadius: 999,
                fontSize: '0.9rem',
                fontWeight: 600,
                fontFamily: 'inherit',
                color: on ? '#0a0a0c' : 'var(--hs-text-body)',
                background: on ? 'var(--hs-orange, #f0583a)' : 'rgba(255,255,255,0.03)',
                border: `1px solid ${on ? 'var(--hs-orange, #f0583a)' : 'rgba(255,255,255,0.14)'}`,
                transition: 'all 0.15s ease',
              }}
            >
              {g.q}
            </button>
          );
        })}
      </div>
      {goal && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: '1.1rem',
            marginTop: '1.5rem',
          }}
        >
          {goal.ids.map((id) => (
            <ProductCard key={id} id={id} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Products(): ReactNode {
  return (
    <Layout
      title="Products — the Zyvor infrastructure suite"
      description={`${platform.products} integrated products for migration, Kubernetes-era VM management, observability, GPU fabric, and bare metal — one API contract across the stack.`}
    >
      <PageHero
        eyebrow="Product suite"
        gradientWord="One platform."
        title="Every layer of your infrastructure."
        subtitle="Migrate, run, observe, and scale"
        description={`${platform.products} integrated products — from VMware exit to KubeVirt day-2, GPU scheduling, and bare metal — sharing one API contract and ${platform.apiEndpoints} endpoints.`}
        primaryCta={{label: 'Compare in the docs matrix', to: '/docs/products'}}
        secondaryCta={{label: 'Talk to us', to: '/contact?intent=demo'}}
      />

      <PageContent>
        <StatGrid
          columns={4}
          stats={[
            {value: String(platform.products), label: 'Products'},
            {value: platform.apiEndpoints, label: 'API Endpoints'},
            {value: platform.dashboardViews, label: 'Dashboard Views'},
            {value: String(platform.cloudProviders), label: 'Cloud Providers'},
          ]}
        />

        <ProductFinder />

        {CATEGORIES.map((cat) => (
          <div key={cat.title} style={{marginTop: '1rem'}}>
            <SectionHeader eyebrow={cat.eyebrow} title={cat.title} subtitle={cat.subtitle} />
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '1.25rem',
                marginTop: '0.5rem',
              }}
            >
              {cat.ids.map((id) => (
                <ProductCard key={id} id={id} />
              ))}
            </div>
          </div>
        ))}
      </PageContent>
    </Layout>
  );
}
