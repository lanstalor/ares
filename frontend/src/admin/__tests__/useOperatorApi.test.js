import { renderHook, act } from '@testing-library/react';
import { useOperatorApi } from '../hooks/useOperatorApi';

describe('useOperatorApi', () => {
  let fetchMock;
  const mockToken = 'test-operator-token';

  beforeEach(() => {
    // Mock localStorage
    const localStorageMock = {
      getItem: jest.fn((key) => {
        if (key === 'ares_operator_token') return mockToken;
        return null;
      }),
      setItem: jest.fn(),
      removeItem: jest.fn(),
      clear: jest.fn(),
    };
    global.localStorage = localStorageMock;

    // Mock fetch
    fetchMock = jest.fn();
    global.fetch = fetchMock;

    // Mock import.meta.env
    global.import = {
      meta: {
        env: {
          VITE_API_BASE_URL: 'http://localhost:8000',
        },
      },
    };
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('getFullState includes Authorization header', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ campaign_id: 'test-id', name: 'Test Campaign' }),
    });

    const { result } = renderHook(() => useOperatorApi());

    await act(async () => {
      await result.current.getFullState('test-campaign-id');
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/operator/campaigns/test-campaign-id/full-state'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: `Bearer ${mockToken}`,
        }),
      }),
    );
  });

  test('patchState calls correct endpoint with updates', async () => {
    const updates = { name: 'Updated Campaign' };
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ...updates, campaign_id: 'test-id' }),
    });

    const { result } = renderHook(() => useOperatorApi());

    await act(async () => {
      await result.current.patchState('test-campaign-id', updates);
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/operator/campaigns/test-campaign-id/state'),
      expect.objectContaining({
        method: 'PATCH',
        body: JSON.stringify(updates),
      }),
    );
  });

  test('getAudit calls correct endpoint', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ issues: [] }),
    });

    const { result } = renderHook(() => useOperatorApi());

    await act(async () => {
      await result.current.getAudit('test-campaign-id');
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/operator/campaigns/test-campaign-id/audit'),
      expect.any(Object),
    );
  });

  test('throws error on non-ok response', async () => {
    const errorMessage = 'Unauthorized';
    fetchMock.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: errorMessage }),
    });

    const { result } = renderHook(() => useOperatorApi());

    await expect(
      act(async () => {
        await result.current.getFullState('test-campaign-id');
      }),
    ).rejects.toThrow(errorMessage);
  });

  test('includes Authorization header with token from localStorage', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ audit_results: [] }),
    });

    const { result } = renderHook(() => useOperatorApi());

    await act(async () => {
      await result.current.getAudit('test-campaign-id');
    });

    const callArgs = fetchMock.mock.calls[0];
    expect(callArgs[1].headers.Authorization).toBe(`Bearer ${mockToken}`);
  });
});
