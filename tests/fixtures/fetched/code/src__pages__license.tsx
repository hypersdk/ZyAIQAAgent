// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import {EMAIL_INFO} from '../data/emails';
import {DEPLOY_LICENSE_TEXT, DEPLOY_LICENSE_VERSION} from '../data/deploy-license';

function downloadDeployLicense(): void {
  const blob = new Blob([DEPLOY_LICENSE_TEXT], {type: 'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'LICENSE';
  anchor.click();
  URL.revokeObjectURL(url);
}
import {LEGAL_ENTITY_INDIA} from '../data/legal-entity-india';
import {ProductPage, PageContent, styles, MarketingHero} from '../components/shared';

type LicenseSection = {
  heading: string;
  body: string;
};

function parseDeployLicense(text: string): {preamble: string; sections: LicenseSection[]} {
  const lines = text.trimEnd().split('\n');
  const sections: LicenseSection[] = [];
  let preambleLines: string[] = [];
  let currentHeading: string | null = null;
  let currentBody: string[] = [];
  let seenSection = false;

  const flush = () => {
    if (currentHeading === null) {
      return;
    }
    sections.push({
      heading: currentHeading,
      body: currentBody.join('\n').trim(),
    });
    currentHeading = null;
    currentBody = [];
  };

  for (const line of lines) {
    const match = line.match(/^(\d+)\.\s+(.+)$/);
    if (match && match[2] === match[2].toUpperCase() && match[2].length > 3) {
      seenSection = true;
      flush();
      currentHeading = `${match[1]}. ${match[2]}`;
      continue;
    }
    if (!seenSection) {
      preambleLines.push(line);
    } else if (currentHeading !== null) {
      currentBody.push(line);
    }
  }
  flush();

  const preamble = preambleLines.join('\n').trim();
  return {preamble, sections};
}

const {preamble, sections} = parseDeployLicense(DEPLOY_LICENSE_TEXT);

export default function LicensePage(): ReactNode {
  return (
    <ProductPage
      title="Proprietary Software License"
      description={`Deploy EULA (v${DEPLOY_LICENSE_VERSION}) for PacketWolf, HyperSDK Platform, and the Zyvor product suite — ${LEGAL_ENTITY_INDIA.legalName}.`}
    >
      <MarketingHero pageId="license" />

      <PageContent>
        <div
          className={styles.featureCard}
          style={{
            textAlign: 'left',
            maxWidth: 900,
            margin: '0 auto 2rem',
            padding: '2rem 2.5rem',
            border: '1px solid rgba(240, 88, 58, 0.2)',
            background: 'rgba(240, 88, 58, 0.03)',
          }}
        >
          <p style={{color: 'var(--hs-text-muted)', fontSize: '0.92rem', lineHeight: 1.7, margin: 0}}>
            <strong style={{color: 'var(--hs-text-heading)'}}>Deploy EULA v{DEPLOY_LICENSE_VERSION}</strong> — governs
            self-hosted binaries, containers, and customer bundles. Hosted platform use is also subject to our{' '}
            <Link to="/terms">Terms of Service</Link> and <Link to="/privacy">Privacy Policy</Link>. See the{' '}
            <Link to="/docs/licensing">licensing docs</Link> for the full framework. Enterprise orders may include a
            separate written agreement.
          </p>
          <p style={{color: 'var(--hs-text-muted)', fontSize: '0.92rem', margin: '1rem 0 0'}}>
            <button
              type="button"
              onClick={downloadDeployLicense}
              style={{
                background: 'none',
                border: 'none',
                padding: 0,
                color: 'var(--hs-accent-light)',
                fontWeight: 600,
                cursor: 'pointer',
                font: 'inherit',
              }}
            >
              Download plain-text LICENSE
            </button>
            {' · '}
            <a href={`mailto:legal@zyvor.dev`}>legal@zyvor.dev</a>
          </p>
        </div>

        <div className={styles.featureCard} style={{textAlign: 'left', maxWidth: 900, margin: '0 auto'}}>
          <pre
            style={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              fontFamily: 'var(--ifm-font-family-monospace)',
              fontSize: '0.82rem',
              lineHeight: 1.65,
              color: 'var(--hs-text-muted)',
              margin: '0 0 2rem',
              padding: 0,
              background: 'transparent',
              border: 'none',
            }}
          >
            {preamble}
          </pre>

          {sections.map((section) => (
            <section key={section.heading} style={{marginBottom: '2rem'}}>
              <h2
                style={{
                  fontSize: '1.05rem',
                  fontWeight: 700,
                  color: 'var(--hs-text-heading)',
                  marginBottom: '0.75rem',
                }}
              >
                {section.heading}
              </h2>
              <pre
                style={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontFamily: 'inherit',
                  fontSize: '0.92rem',
                  lineHeight: 1.75,
                  color: 'var(--hs-text-muted)',
                  margin: 0,
                  padding: 0,
                  background: 'transparent',
                  border: 'none',
                }}
              >
                {section.body}
              </pre>
            </section>
          ))}

          <p style={{color: 'var(--ifm-color-emphasis-600)', marginTop: '2rem'}}>
            Questions about licensing: <a href={`mailto:${EMAIL_INFO}`}>{EMAIL_INFO}</a> ·{' '}
            <Link to="/contact">Contact</Link>
          </p>
        </div>
      </PageContent>
    </ProductPage>
  );
}
