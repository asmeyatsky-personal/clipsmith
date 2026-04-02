import { apiClient } from './client';

// ==================== Response Types ====================

export interface HashtagFormatted {
    original: string;
    camel_case: string;
    readable: string;
    title_case: string;
    short: string;
}

export interface TrendingHashtag {
    name: string;
    count: number;
    trending_score: number;
    last_used_at: string | null;
    formatted: HashtagFormatted;
    created_at: string;
}

export interface TrendingHashtagsResponse {
    hashtags: TrendingHashtag[];
    timeframe_hours: number;
    total: number;
}

export interface PopularHashtag {
    name: string;
    count: number;
    formatted: HashtagFormatted;
    created_at: string;
}

export interface PopularHashtagsResponse {
    hashtags: PopularHashtag[];
    total: number;
}

export interface SearchHashtag {
    name: string;
    formatted: HashtagFormatted;
}

export interface SearchHashtagsResponse {
    hashtags: SearchHashtag[];
    total: number;
    query: string;
}

export interface RecentHashtag {
    name: string;
    count: number;
    last_used_at: string | null;
    created_at: string;
}

export interface RecentHashtagsResponse {
    hashtags: RecentHashtag[];
    timeframe_hours: number;
    total: number;
}

export interface HashtagDetail {
    name: string;
    count: number;
    trending_score: number;
    last_used_at: string | null;
    created_at: string;
}

// ==================== Service ====================

export const hashtagService = {
    async getTrending(params?: {
        hours?: number;
        limit?: number;
    }): Promise<TrendingHashtagsResponse> {
        const searchParams = new URLSearchParams();
        if (params?.hours) searchParams.set('hours', params.hours.toString());
        if (params?.limit) searchParams.set('limit', params.limit.toString());
        const query = searchParams.toString();
        return apiClient<TrendingHashtagsResponse>(`/hashtags/trending${query ? `?${query}` : ''}`);
    },

    async getPopular(limit?: number): Promise<PopularHashtagsResponse> {
        const params = limit ? `?limit=${limit}` : '';
        return apiClient<PopularHashtagsResponse>(`/hashtags/popular${params}`);
    },

    async search(q: string, limit?: number): Promise<SearchHashtagsResponse> {
        const searchParams = new URLSearchParams({ q });
        if (limit) searchParams.set('limit', limit.toString());
        return apiClient<SearchHashtagsResponse>(`/hashtags/search?${searchParams.toString()}`);
    },

    async getRecent(params?: {
        hours?: number;
        limit?: number;
    }): Promise<RecentHashtagsResponse> {
        const searchParams = new URLSearchParams();
        if (params?.hours) searchParams.set('hours', params.hours.toString());
        if (params?.limit) searchParams.set('limit', params.limit.toString());
        const query = searchParams.toString();
        return apiClient<RecentHashtagsResponse>(`/hashtags/recent${query ? `?${query}` : ''}`);
    },

    async getDetails(hashtagName: string): Promise<HashtagDetail> {
        return apiClient<HashtagDetail>(`/hashtags/${encodeURIComponent(hashtagName)}`);
    },
};
