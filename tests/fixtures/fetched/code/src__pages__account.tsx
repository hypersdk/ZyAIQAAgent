// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import {type ReactNode, useMemo} from 'react';
import Head from '@docusaurus/Head';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {ProductPage, MarketingHero, PageContent} from '../components/shared';
import {useFirebaseAuth} from '../hooks/useFirebaseAuth';
import S from './account.module.css';

export default function AccountPage(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  const customFields = useMemo(
    () => (siteConfig.customFields ?? {}) as Record<string, unknown>,
    [siteConfig.customFields],
  );
  const {cfg, user, loading, error, signIn, logout, clearError} = useFirebaseAuth(customFields);

  return (
    <ProductPage title="Account" description="Sign in with Google, GitHub, Facebook, or LinkedIn.">
      <Head>
        <meta name="robots" content="noindex, nofollow" />
      </Head>
      <MarketingHero pageId="account" />
      <PageContent>
        <div className={S.wrap}>
          <div className={S.card}>
            <h2 className={S.title}>Sign in</h2>
            <p className={S.sub}>
              OAuth sign-in powered by{' '}
              <a href="https://firebase.google.com/docs/auth" rel="noopener noreferrer">
                Firebase Authentication
              </a>
              . Profiles sync to{' '}
              <a href="https://firebase.google.com/docs/firestore" rel="noopener noreferrer">
                Cloud Firestore
              </a>{' '}
              (NoSQL) under <code>users/&lt;uid&gt;</code>.
            </p>

            {!cfg && (
              <div className={S.notice}>
                <strong>Firebase is not configured for this build.</strong> Set the <code>FIREBASE_*</code> variables at
                build time (see <code>auth.firebase.env.example</code>), enable providers in the Firebase console, and
                deploy Firestore rules from <code>firestore.rules</code>.
              </div>
            )}

            {error && (
              <div className={S.err} role="alert">
                {error}{' '}
                <button type="button" className={S.signOut} onClick={clearError}>
                  Dismiss
                </button>
              </div>
            )}

            {cfg && !user && (
              <>
                <div className={S.btnRow}>
                  <button type="button" className={S.oauthBtn} disabled={loading} onClick={() => void signIn('google')}>
                    Google
                  </button>
                  <button type="button" className={S.oauthBtn} disabled={loading} onClick={() => void signIn('github')}>
                    GitHub
                  </button>
                  <button
                    type="button"
                    className={S.oauthBtn}
                    disabled={loading}
                    onClick={() => void signIn('facebook')}
                  >
                    Facebook
                  </button>
                  <button
                    type="button"
                    className={S.oauthBtn}
                    disabled={loading}
                    onClick={() => void signIn('linkedin')}
                  >
                    LinkedIn
                  </button>
                </div>
                {loading && <p className={S.sub}>Checking session…</p>}
              </>
            )}

            {user && (
              <>
                <div className={S.profile}>
                  {user.photoURL ? (
                    <img className={S.avatar} src={user.photoURL} alt="" width={56} height={56} />
                  ) : (
                    <div className={S.avatar} aria-hidden style={{background: 'rgba(240,88,58,0.25)'}} />
                  )}
                  <div className={S.profileText}>
                    <p className={S.profileName}>{user.displayName || 'Signed in'}</p>
                    <p className={S.profileMeta}>{user.email}</p>
                    <p className={S.profileMeta}>UID: {user.uid}</p>
                  </div>
                </div>
                <button type="button" className={S.signOut} onClick={() => void logout()}>
                  Sign out
                </button>
              </>
            )}
          </div>
        </div>
      </PageContent>
    </ProductPage>
  );
}
