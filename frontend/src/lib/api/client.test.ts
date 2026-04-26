import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient, getBaseUrl } from './client';

vi.mock('@/lib/auth/auth-store', () => ({
    useAuthStore: {
        getState: () => ({
            logout: vi.fn(),
        }),
    },
}));

describe('apiClient', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    it('hits the configured base URL', async () => {
        const mockFetch = vi.fn().mockResolvedValue({
            ok: true,
            status: 200,
            json: async () => ({ ping: 'pong' }),
        });
        vi.stubGlobal('fetch', mockFetch);
        const result = await apiClient<{ ping: string }>('/health');
        expect(result.ping).toBe('pong');
        const url = mockFetch.mock.calls[0][0];
        expect(url).toBe(`${getBaseUrl()}/health`);
    });

    it('throws on 4xx', async () => {
        vi.stubGlobal(
            'fetch',
            vi.fn().mockResolvedValue({
                ok: false,
                status: 400,
                json: async () => ({ detail: 'bad' }),
            }),
        );
        await expect(apiClient('/x')).rejects.toThrow('bad');
    });
});
