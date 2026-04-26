import { apiClient } from './client';
import { VideoResponseDTO, PaginatedVideos } from '../types';

interface TipResponseDTO {
    id: string;
    sender_id: string;
    receiver_id: string;
    video_id: string;
    amount: number;
    currency: string;
}

export const videoService = {
    async getById(videoId: string): Promise<VideoResponseDTO> {
        return await apiClient<VideoResponseDTO>(`/videos/${videoId}`);
    },

    async generateCaptions(videoId: string): Promise<{ message: string; video_id: string }> {
        return await apiClient<{ message: string; video_id: string }>(`/videos/${videoId}/captions/generate`, {
            method: 'POST',
        });
    },

    async sendTip(videoId: string, receiverId: string, amount: number): Promise<TipResponseDTO> {
        return await apiClient<TipResponseDTO>(`/videos/${videoId}/tip`, {
            method: 'POST',
            body: JSON.stringify({
                receiver_id: receiverId,
                video_id: videoId,
                amount: amount,
                currency: "USD"
            })
        });
    },

    async incrementViews(videoId: string): Promise<{ views: number }> {
        return await apiClient<{ views: number }>(`/videos/${videoId}/view`, {
            method: 'POST',
        });
    },

    async search(query: string, page: number = 1, pageSize: number = 20): Promise<PaginatedVideos> {
        // Backend returns PaginatedVideoResponseDTO ({items, total, total_pages, page, page_size}).
        // The frontend has historically used PaginatedVideos ({videos, has_more, ...}) — adapt.
        const raw = await apiClient<{ items: VideoResponseDTO[]; total: number; page: number; page_size: number; total_pages: number }>(
            `/videos/search?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`,
        );
        return {
            videos: raw.items,
            total: raw.total,
            page: raw.page,
            page_size: raw.page_size,
            has_more: raw.page < raw.total_pages,
        };
    },

    async getCaptions(videoId: string): Promise<CaptionDTO[]> {
        return await apiClient<CaptionDTO[]>(`/videos/${videoId}/captions`);
    },

    async getChapters(videoId: string): Promise<{ items: ChapterMarker[] }> {
        return await apiClient<{ items: ChapterMarker[] }>(`/videos/${videoId}/chapters`);
    },

    async detectScenes(videoId: string): Promise<{ queued: boolean }> {
        return await apiClient<{ queued: boolean }>(
            `/videos/${videoId}/scenes/detect`,
            { method: 'POST' },
        );
    },

    async enhanceVoice(videoId: string): Promise<{ queued: boolean }> {
        return await apiClient<{ queued: boolean }>(
            `/videos/${videoId}/voice/enhance`,
            { method: 'POST' },
        );
    },
};

export interface ChapterMarker {
    id: string;
    title: string;
    start_time: number;
    end_time: number;
    auto: boolean;
}

export interface CaptionDTO {
    id: string;
    video_id: string;
    text: string;
    start_time: number;
    end_time: number;
    language: string;
}
