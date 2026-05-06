import { useState, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const API_PREFIX = `${API_BASE_URL}/api/v1`;

export function useOperatorApi() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const getToken = useCallback(() => {
    if (typeof localStorage === 'undefined') return null;
    return localStorage.getItem('ares_operator_token');
  }, []);

  const request = useCallback(
    async (path, options = {}, fallbackMessage = 'Request failed') => {
      setIsLoading(true);
      setError(null);

      try {
        const token = getToken();
        const headers = {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...(options.headers ?? {}),
        };

        const response = await fetch(`${API_PREFIX}${path}`, {
          ...options,
          headers,
        });

        if (!response.ok) {
          let detail = fallbackMessage;
          try {
            const payload = await response.json();
            if (typeof payload?.detail === 'string' && payload.detail.trim()) {
              detail = payload.detail;
            }
          } catch {
            // Ignore JSON parsing failures and keep the fallback message.
          }

          throw new Error(detail);
        }

        return await response.json();
      } finally {
        setIsLoading(false);
      }
    },
    [getToken],
  );

  const getFullState = useCallback(
    (campaignId) => {
      return request(
        `/operator/campaigns/${campaignId}/full-state`,
        {},
        'Failed to fetch full state',
      );
    },
    [request],
  );

  const patchState = useCallback(
    (campaignId, updates) => {
      return request(
        `/operator/campaigns/${campaignId}/state`,
        {
          method: 'PATCH',
          body: JSON.stringify(updates),
        },
        'Failed to patch state',
      );
    },
    [request],
  );

  const getAudit = useCallback(
    (campaignId) => {
      return request(
        `/operator/campaigns/${campaignId}/audit`,
        {},
        'Failed to fetch audit',
      );
    },
    [request],
  );

  return {
    getFullState,
    patchState,
    getAudit,
    isLoading,
    error,
  };
}
