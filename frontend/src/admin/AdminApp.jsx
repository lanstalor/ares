import { createContext, useContext, useEffect, useState } from 'react';
import { useOperatorApi } from './hooks/useOperatorApi';
import AdminLogin from './AdminLogin';
import AdminSidebar from './components/AdminSidebar';
import CampaignPage from './pages/CampaignPage';
import ObjectivesPage from './pages/ObjectivesPage';
import ClocksPage from './pages/ClocksPage';
import SecretsPage from './pages/SecretsPage';
import NPCsPage from './pages/NPCsPage';

const OperatorStateContext = createContext(null);

export function useOperatorState() {
  const context = useContext(OperatorStateContext);
  if (!context) {
    throw new Error('useOperatorState must be used within AdminApp');
  }
  return context;
}

export default function AdminApp() {
  const api = useOperatorApi();
  const [token, setToken] = useState(() => {
    if (typeof localStorage === 'undefined') return null;
    return localStorage.getItem('ares_operator_token');
  });
  const [fullState, setFullState] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activePage, setActivePage] = useState('Campaign');

  const campaignId = fullState?.campaign_id || 'test-campaign';

  // Load full state when token is present
  useEffect(() => {
    if (!token) {
      setFullState(null);
      return;
    }

    let isMounted = true;

    async function loadFullState() {
      setIsLoading(true);
      setError(null);

      try {
        const state = await api.getFullState(campaignId);
        if (isMounted) {
          setFullState(state);
        }
      } catch (err) {
        if (isMounted) {
          // Handle 401/403 by clearing token
          if (err.message.includes('Unauthorized') || err.message.includes('403')) {
            localStorage.removeItem('ares_operator_token');
            setToken(null);
          }
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadFullState();

    return () => {
      isMounted = false;
    };
  }, [token, campaignId, api]);

  function handleTokenSubmit(newToken) {
    localStorage.setItem('ares_operator_token', newToken);
    setToken(newToken);
  }

  function handleLogout() {
    localStorage.removeItem('ares_operator_token');
    setToken(null);
    setFullState(null);
    setActivePage('Campaign');
  }

  // Show login if no token
  if (!token) {
    return (
      <AdminLogin
        onTokenSubmit={handleTokenSubmit}
        isLoading={api.isLoading}
        error={api.error}
      />
    );
  }

  // Show loading state
  if (!fullState && isLoading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingContent}>
          <p>Loading operator state...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && !fullState) {
    return (
      <div style={styles.container}>
        <div style={styles.errorContent}>
          <p style={styles.errorText}>Error: {error}</p>
          <button
            onClick={handleLogout}
            style={styles.errorButton}
          >
            Logout
          </button>
        </div>
      </div>
    );
  }

  // Render main admin interface
  return (
    <OperatorStateContext.Provider
      value={{
        fullState,
        api,
        isLoading,
        error,
        campaignId,
        onRefreshState: () => {
          // Trigger a refetch
          setFullState(null);
        },
      }}
    >
      <div style={styles.container}>
        <AdminSidebar
          activePage={activePage}
          onPageChange={setActivePage}
          onLogout={handleLogout}
        />

        <div style={styles.mainContent}>
          <div style={styles.pageContent}>
            {activePage === 'Campaign' && <CampaignPage />}
            {activePage === 'Objectives' && <ObjectivesPage />}
            {activePage === 'Clocks' && <ClocksPage />}
            {activePage === 'Secrets' && <SecretsPage />}
            {activePage === 'NPCs' && <NPCsPage />}
          </div>
        </div>
      </div>
    </OperatorStateContext.Provider>
  );
}

const styles = {
  container: {
    display: 'flex',
    minHeight: '100vh',
    backgroundColor: '#0a0e27',
    color: '#e5eaf1',
    fontFamily: '"VT323", monospace',
  },
  loadingContent: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.125rem',
    color: '#b0c4e4',
  },
  errorContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
    gap: '1.5rem',
  },
  errorText: {
    color: '#ff8b92',
    textAlign: 'center',
    maxWidth: '500px',
  },
  errorButton: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#ff6b35',
    border: 'none',
    color: '#0a0e27',
    fontFamily: '"VT323", monospace',
    fontSize: '1rem',
    fontWeight: 'bold',
    cursor: 'pointer',
    borderRadius: '2px',
  },
  mainContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'auto',
  },
  pageContent: {
    padding: '2rem',
    flex: 1,
    overflow: 'auto',
  },
};
