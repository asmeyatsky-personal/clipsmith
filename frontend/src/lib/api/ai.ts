import { apiClient } from './client';

// ==================== Response Types ====================

export interface CaptionGenerateResponse {
    success: boolean;
    job_id: string;
    message: string;
}

export interface CaptionJobResponse {
    id: string;
    status: string;
    language: string;
    captions: Record<string, unknown>[] | null;
    error_message: string | null;
    created_at: string | null;
    completed_at: string | null;
}

export interface AITemplate {
    id: string;
    name: string;
    description: string;
    category: string;
    style: string;
    thumbnail_url: string | null;
    is_premium: boolean;
    price: number;
    usage_count: number;
    tags: string[];
}

export interface AITemplateDetail extends AITemplate {
    project_data: Record<string, unknown>;
}

export interface TemplatesResponse {
    templates: AITemplate[];
}

export interface CreateTemplateResponse {
    success: boolean;
    template_id: string;
}

export interface UseTemplateResponse {
    success: boolean;
    project_id: string;
    message: string;
}

export interface VideoGenerateResponse {
    success: boolean;
    job_id: string;
    message: string;
}

export interface VideoGenerationJobResponse {
    id: string;
    status: string;
    generation_type: string;
    prompt: string;
    result_url: string | null;
    error_message: string | null;
    created_at: string | null;
    completed_at: string | null;
}

export interface VoiceOverGenerateResponse {
    success: boolean;
    job_id: string;
    message: string;
}

export interface VoiceOverJobResponse {
    id: string;
    status: string;
    text: string;
    voice_id: string;
    result_url: string | null;
    error_message: string | null;
    created_at: string | null;
    completed_at: string | null;
}

export interface Voice {
    id: string;
    name: string;
    language: string;
    gender: string;
}

export interface VoicesResponse {
    voices: Voice[];
}

// ==================== Service ====================

export const aiService = {
    // AI Captions
    async generateCaptions(data: {
        project_id: string;
        video_asset_id: string;
        language?: string;
    }): Promise<CaptionGenerateResponse> {
        return apiClient<CaptionGenerateResponse>('/api/ai/captions/generate', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getCaptionJob(jobId: string): Promise<CaptionJobResponse> {
        return apiClient<CaptionJobResponse>(`/api/ai/captions/${jobId}`);
    },

    // AI Templates
    async listTemplates(params?: {
        category?: string;
        style?: string;
        is_premium?: boolean;
        limit?: number;
        offset?: number;
    }): Promise<TemplatesResponse> {
        const searchParams = new URLSearchParams();
        if (params?.category) searchParams.set('category', params.category);
        if (params?.style) searchParams.set('style', params.style);
        if (params?.is_premium !== undefined) searchParams.set('is_premium', String(params.is_premium));
        if (params?.limit) searchParams.set('limit', params.limit.toString());
        if (params?.offset) searchParams.set('offset', params.offset.toString());
        return apiClient<TemplatesResponse>(`/api/ai/templates?${searchParams.toString()}`);
    },

    async getTemplate(templateId: string): Promise<AITemplateDetail> {
        return apiClient<AITemplateDetail>(`/api/ai/templates/${templateId}`);
    },

    async createTemplate(data: {
        name: string;
        description?: string;
        category?: string;
        style?: string;
        thumbnail_url?: string;
        project_data?: Record<string, unknown>;
        is_premium?: boolean;
        price?: number;
        is_public?: boolean;
        tags?: string[];
    }): Promise<CreateTemplateResponse> {
        return apiClient<CreateTemplateResponse>('/api/ai/templates', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async useTemplate(templateId: string, data: {
        title?: string;
        description?: string;
    }): Promise<UseTemplateResponse> {
        return apiClient<UseTemplateResponse>(`/api/ai/templates/${templateId}/use`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // AI Video Generation
    async generateVideo(data: {
        project_id?: string;
        generation_type?: string;
        prompt: string;
        negative_prompt?: string;
        duration?: number;
        model_version?: string;
        settings?: Record<string, unknown>;
    }): Promise<VideoGenerateResponse> {
        return apiClient<VideoGenerateResponse>('/api/ai/video/generate', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getVideoGenerationJob(jobId: string): Promise<VideoGenerationJobResponse> {
        return apiClient<VideoGenerationJobResponse>(`/api/ai/video/${jobId}`);
    },

    // AI Voice Over
    async generateVoiceOver(data: {
        project_id?: string;
        text: string;
        voice_id?: string;
        language?: string;
        speed?: number;
    }): Promise<VoiceOverGenerateResponse> {
        return apiClient<VoiceOverGenerateResponse>('/api/ai/voiceover/generate', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getVoiceOverJob(jobId: string): Promise<VoiceOverJobResponse> {
        return apiClient<VoiceOverJobResponse>(`/api/ai/voiceover/${jobId}`);
    },

    async listVoices(language?: string): Promise<VoicesResponse> {
        const params = language ? `?language=${encodeURIComponent(language)}` : '';
        return apiClient<VoicesResponse>(`/api/ai/voices${params}`);
    },
};
