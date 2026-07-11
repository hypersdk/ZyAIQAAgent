// Copyright (c) 2026 ZyvorAI Labs Private Limited. All rights reserved.
// Proprietary software — see LICENSE in the repository root.
// https://zyvor.dev · info@zyvor.dev

import React, {useState, useEffect, useCallback, type ReactNode} from 'react';
import Layout from '@theme/Layout';
import Head from '@docusaurus/Head';
import {MarketingHero} from '../components/shared';
import {LoginForm} from '../components/admin/LoginForm';
import {OverviewTab} from '../components/admin/OverviewTab';
import {MessagesTab} from '../components/admin/MessagesTab';
import {AnalyticsTab} from '../components/admin/AnalyticsTab';
import {PulseTab} from '../components/admin/PulseTab';
import {YouTubeTab} from '../components/admin/YouTubeTab';
import {DownloadsTab} from '../components/admin/DownloadsTab';
import {LeadsTab} from '../components/admin/LeadsTab';
import {ADMIN_API_BASE} from '../components/admin/constants';
import S from './admin.module.css';

type TabId = 'overview' | 'messages' | 'analytics' | 'pulse' | 'youtube' | 'downloads' | 'leads';

export default function AdminPage(): ReactNode {
  const [token, setToken] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [pulseVisitorId, setPulseVisitorId] = useState<number | undefined>();

  const openPulseVisitor = useCallback((visitorId: number) => {
    setPulseVisitorId(visitorId);
    setActiveTab('pulse');
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('youtube') === 'connected') {
      setActiveTab('youtube');
      window.history.replaceState({}, '', '/admin');
    }
    const stored = sessionStorage.getItem('admin_token');
    if (!stored) return;
    fetch(`${ADMIN_API_BASE}/api/v1/admin/dashboard`, {
      headers: {'X-Admin-Token': stored},
    })
      .then((res) => {
        if (res.ok) {
          setToken(stored);
        } else {
          sessionStorage.removeItem('admin_token');
        }
      })
      .catch(() => {
        setToken(stored);
      });
  }, []);

  const handleLogout = () => {
    sessionStorage.removeItem('admin_token');
    setToken(null);
  };

  const tabs: {id: TabId; label: string}[] = [
    {id: 'overview', label: 'Overview'},
    {id: 'messages', label: 'Messages'},
    {id: 'analytics', label: 'Analytics'},
    {id: 'downloads', label: 'Downloads'},
    {id: 'leads', label: 'Leads'},
    {id: 'pulse', label: 'Pulse'},
    {id: 'youtube', label: 'YouTube'},
  ];

  return (
    <Layout title="Admin Panel | HyperSDK Platform" description="HyperSDK Platform Admin Panel">
      <Head>
        <meta name="robots" content="noindex, nofollow" />
      </Head>

      <MarketingHero pageId="admin" />

      <div className={S.page}>
        {!token ? (
          <LoginForm onLogin={setToken} />
        ) : (
          <>
            <div className={S.topBar}>
              <div className={S.topBarTitle}>
                <span style={{color: '#f0583a'}}>&#9670;</span>
                Admin Panel
              </div>
              <button type="button" className={S.logoutBtn} onClick={handleLogout}>
                Logout
              </button>
            </div>

            <div className={S.tabBar}>
              {tabs.map((t) => (
                <button
                  type="button"
                  key={t.id}
                  className={activeTab === t.id ? S.tabActive : S.tab}
                  onClick={() => setActiveTab(t.id)}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <div className={S.content}>
              {activeTab === 'overview' && <OverviewTab token={token} onOpenPulseVisitor={openPulseVisitor} />}
              {activeTab === 'messages' && <MessagesTab token={token} />}
              {activeTab === 'analytics' && <AnalyticsTab token={token} onOpenPulseVisitor={openPulseVisitor} />}
              {activeTab === 'downloads' && <DownloadsTab token={token} />}
              {activeTab === 'leads' && <LeadsTab token={token} />}
              {activeTab === 'pulse' && (
                <PulseTab
                  token={token}
                  initialVisitorId={pulseVisitorId}
                  onInitialVisitorConsumed={() => setPulseVisitorId(undefined)}
                />
              )}
              {activeTab === 'youtube' && <YouTubeTab token={token} />}
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
