// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import {type ReactNode, useId, useState, useMemo, type KeyboardEvent} from 'react';
import {useRovingFocus} from '../hooks/useRovingFocus';
import Head from '@docusaurus/Head';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {EMAIL_INFO, EMAIL_SALES} from '../data/emails';
import {buildFaqPageJsonLd, getFaqPageData, type FaqPageItem} from '../data/faq-page-locale';
import {ProductPage, MarketingHero, PageContent, CTASection, styles} from '../components/shared';

function FaqAccordionItem({
  item,
  index,
  groupId,
  defaultOpen = false,
  setRef,
  onGroupKeyDown,
}: {
  item: FaqPageItem;
  index: number;
  groupId: string;
  defaultOpen?: boolean;
  setRef: (index: number) => (el: HTMLButtonElement | null) => void;
  onGroupKeyDown: (event: KeyboardEvent, index: number) => void;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const questionId = `${groupId}-q-${index}`;
  const answerId = `${groupId}-a-${index}`;

  const toggle = () => setOpen((v) => !v);

  const onKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggle();
      return;
    }
    onGroupKeyDown(event, index);
  };

  return (
    <div
      className={styles.featureCard}
      style={{
        marginBottom: '0.75rem',
        border: open ? '1px solid rgba(240,88,58,0.25)' : undefined,
        padding: 0,
      }}
    >
      <button
        ref={setRef(index)}
        type="button"
        onClick={toggle}
        onKeyDown={onKeyDown}
        aria-expanded={open}
        aria-controls={answerId}
        id={questionId}
        style={{
          width: '100%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          minHeight: '44px',
          padding: '1.25rem 1.5rem',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          textAlign: 'left',
        }}
      >
        <span
          style={{color: 'var(--hs-text-heading)', fontWeight: 600, fontSize: '1rem', flex: 1, paddingRight: '1rem'}}
        >
          {item.q}
        </span>
        <span
          aria-hidden
          style={{
            color: 'var(--hs-accent)',
            fontSize: '1.2rem',
            fontWeight: 700,
            transform: open ? 'rotate(45deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s ease',
            flexShrink: 0,
          }}
        >
          +
        </span>
      </button>
      <div
        id={answerId}
        role="region"
        aria-labelledby={questionId}
        hidden={!open}
        style={{padding: open ? '0 1.5rem 1.25rem' : 0}}
      >
        <p style={{color: 'var(--hs-text-muted)', fontSize: '0.95rem', lineHeight: 1.7, margin: 0}}>{item.a}</p>
      </div>
    </div>
  );
}

function FaqAccordionGroup({items, openFirst = false}: {items: FaqPageItem[]; openFirst?: boolean}) {
  const groupId = useId();
  const {setRef, handleKeyDown} = useRovingFocus(items.length);

  return (
    <>
      {items.map((item, index) => (
        <FaqAccordionItem
          key={item.q}
          item={item}
          index={index}
          groupId={groupId}
          defaultOpen={openFirst && index === 0}
          setRef={setRef}
          onGroupKeyDown={handleKeyDown}
        />
      ))}
    </>
  );
}

export default function FaqPage(): ReactNode {
  const {i18n} = useDocusaurusContext();
  const {popular: popularQuestions, categories, ui} = getFaqPageData(i18n.currentLocale);
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!search.trim()) return categories;
    const q = search.toLowerCase();
    return categories
      .map((cat) => ({
        ...cat,
        items: cat.items.filter((i) => i.q.toLowerCase().includes(q) || i.a.toLowerCase().includes(q)),
      }))
      .filter((cat) => cat.items.length > 0);
  }, [search, categories]);

  const filteredPopular = useMemo(() => {
    if (!search.trim()) return popularQuestions;
    const q = search.toLowerCase();
    return popularQuestions.filter((i) => i.q.toLowerCase().includes(q) || i.a.toLowerCase().includes(q));
  }, [search, popularQuestions]);

  const faqJsonLd = buildFaqPageJsonLd(i18n.currentLocale);

  return (
    <ProductPage
      title="FAQ"
      description="Frequently asked questions about HyperSDK Platform enterprise VM migration platform."
    >
      <Head>
        <script type="application/ld+json">{JSON.stringify(faqJsonLd)}</script>
      </Head>
      <MarketingHero pageId="faq" />

      <PageContent>
        <div style={{maxWidth: 850, margin: '0 auto'}}>
          <div style={{marginBottom: '2.5rem'}}>
            <input
              type="search"
              placeholder={ui.searchPlaceholder}
              aria-label={ui.searchPlaceholder}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className={styles.formInput}
              style={{
                width: '100%',
                padding: '1rem 1.5rem',
                fontSize: '1rem',
              }}
            />
          </div>

          {filteredPopular.length > 0 && (
            <div style={{marginBottom: '3rem'}}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  marginBottom: '1.25rem',
                }}
              >
                <h2
                  className={styles.monoLabel}
                  style={{
                    paddingLeft: '0.25rem',
                    margin: 0,
                    color: 'var(--hs-accent-light)',
                  }}
                >
                  {ui.mostAsked}
                </h2>
                <span
                  style={{
                    background: 'rgba(255, 140, 0, 0.1)',
                    color: 'var(--hs-accent-light)',
                    padding: '0.2rem 0.6rem',
                    borderRadius: 6,
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    border: '1px solid rgba(255, 140, 0, 0.2)',
                  }}
                >
                  {ui.top5Badge}
                </span>
              </div>
              <FaqAccordionGroup items={filteredPopular} openFirst />
            </div>
          )}

          {filtered.map((cat) => (
            <div key={cat.title} style={{marginBottom: '2.5rem'}}>
              <h2 className={styles.monoLabel} style={{paddingLeft: '0.25rem', marginBottom: '1.25rem'}}>
                {cat.title}
              </h2>
              <FaqAccordionGroup items={cat.items} />
            </div>
          ))}

          {filtered.length === 0 && filteredPopular.length === 0 && (
            <div style={{textAlign: 'center', padding: '3rem'}}>
              <p style={{color: 'var(--hs-text-subtle)', fontSize: '1.1rem'}}>{ui.noResults}</p>
            </div>
          )}

          <div
            className={styles.featureCard}
            style={{
              padding: '2.5rem',
              textAlign: 'center',
              marginTop: '2rem',
              marginBottom: '3rem',
              border: '1px solid rgba(255, 140, 0, 0.15)',
            }}
          >
            <h2
              style={{
                fontSize: '1.5rem',
                fontWeight: 700,
                color: 'var(--hs-text-heading)',
                marginBottom: '1rem',
              }}
            >
              {ui.didntFindTitle}
            </h2>
            <p
              style={{
                color: 'var(--hs-text-muted)',
                fontSize: '0.95rem',
                lineHeight: 1.7,
                marginBottom: '1.5rem',
                maxWidth: 500,
                margin: '0 auto 1.5rem',
              }}
            >
              {ui.didntFindBody}
            </p>
            <div
              style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '1.5rem',
                flexWrap: 'wrap',
              }}
            >
              <a
                href={`mailto:${EMAIL_INFO}`}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  color: 'var(--hs-accent-light)',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  textDecoration: 'none',
                  padding: '0.6rem 1.25rem',
                  borderRadius: 8,
                  border: '1px solid rgba(255, 140, 0, 0.2)',
                  background: 'rgba(255, 140, 0, 0.05)',
                }}
              >
                {EMAIL_INFO}
              </a>
              <a
                href={`mailto:${EMAIL_SALES}`}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  color: 'var(--hs-accent-light)',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  textDecoration: 'none',
                  padding: '0.6rem 1.25rem',
                  borderRadius: 8,
                  border: '1px solid rgba(255, 140, 0, 0.2)',
                  background: 'rgba(255, 140, 0, 0.05)',
                }}
              >
                {EMAIL_SALES} {ui.salesSuffix}
              </a>
              <Link
                to="/contact"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  color: 'var(--hs-accent-light)',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  textDecoration: 'none',
                  padding: '0.6rem 1.25rem',
                  borderRadius: 8,
                  border: '1px solid rgba(255, 140, 0, 0.2)',
                  background: 'rgba(255, 140, 0, 0.05)',
                }}
              >
                {ui.contactForm}
              </Link>
              <Link
                to="/docs/intro"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  color: '#a78bfa',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  textDecoration: 'none',
                  padding: '0.6rem 1.25rem',
                  borderRadius: 8,
                  border: '1px solid rgba(167, 139, 250, 0.2)',
                  background: 'rgba(167, 139, 250, 0.05)',
                }}
              >
                {ui.documentation}
              </Link>
            </div>
          </div>
        </div>

        <CTASection
          title={ui.ctaTitle}
          subtitle={ui.ctaSubtitle}
          primaryCta={{label: ui.ctaPrimary, to: '/contact?intent=demo'}}
          secondaryCta={{label: ui.ctaSecondary, to: '/contact?intent=faq'}}
        />
      </PageContent>
    </ProductPage>
  );
}
