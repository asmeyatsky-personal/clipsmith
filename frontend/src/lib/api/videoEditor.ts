import { apiClient } from './client';

// ==================== Response Types ====================

export interface VideoProject {
    id: string;
    user_id: string;
    title: string;
    description: string | null;
    status: string;
    duration: number | null;
    thumbnail_url: string | null;
    published_at: string | null;
    [key: string]: unknown;
}

export interface ProjectResponse {
    success: boolean;
    project: VideoProject;
}

export interface ProjectsResponse {
    success: boolean;
    projects: VideoProject[];
}

export interface VideoAsset {
    id: string;
    project_id: string;
    asset_type: string;
    filename: string;
    file_size: number;
    mime_type: string;
    url: string;
    [key: string]: unknown;
}

export interface AssetResponse {
    success: boolean;
    asset: VideoAsset;
}

export interface AssetsResponse {
    success: boolean;
    assets: VideoAsset[];
}

export interface Transition {
    id: string;
    project_id: string;
    transition_type: string;
    start_time: number;
    end_time: number;
    duration: number;
    parameters: Record<string, unknown> | null;
    [key: string]: unknown;
}

export interface TransitionResponse {
    success: boolean;
    transition: Transition;
}

export interface TransitionsResponse {
    success: boolean;
    transitions: Transition[];
}

export interface Track {
    id: string;
    project_id: string;
    asset_id: string;
    track_type: string;
    start_time: number;
    end_time: number;
    [key: string]: unknown;
}

export interface TrackResponse {
    success: boolean;
    track: Track;
}

export interface TracksResponse {
    success: boolean;
    tracks: Track[];
}

export interface EditorCaption {
    id: string;
    project_id: string;
    video_asset_id: string;
    text: string;
    start_time: number;
    end_time: number;
    [key: string]: unknown;
}

export interface CaptionResponse {
    success: boolean;
    caption: EditorCaption;
}

export interface CaptionsResponse {
    success: boolean;
    captions: EditorCaption[];
}

export interface MonetizationSettings {
    tips_enabled: boolean;
    subscriptions_enabled: boolean;
    suggested_tip_amounts: number[];
    subscription_price: number;
    subscription_tier_name: string;
}

export interface MonetizationUpdateResponse extends MonetizationSettings {
    success: boolean;
}

export interface PublishResponse {
    success: boolean;
    message: string;
    project_id: string;
    published_at: string;
}

export interface ExportResponse {
    success: boolean;
    message: string;
    project_id: string;
    export_settings: {
        format: string;
        quality: string;
        status: string;
    };
}

export interface ExportStatusResponse {
    project_id: string;
    export_status: string;
    video_url: string | null;
}

export interface DuplicateResponse {
    success: boolean;
    project_id: string;
    message: string;
}

export interface Keyframe {
    id: string;
    property_name: string;
    time: number;
    value: unknown;
    easing: string;
}

export interface KeyframesResponse {
    keyframes: Keyframe[];
}

export interface KeyframeCreateResponse {
    success: boolean;
    keyframe_id: string;
}

export interface ColorGrade {
    brightness: number;
    contrast: number;
    saturation: number;
    temperature?: number;
    tint?: number;
    highlights?: number;
    shadows?: number;
    vibrance?: number;
    filters?: string[];
}

export interface ColorGradeCreateResponse {
    success: boolean;
    color_grade_id: string;
}

export interface AudioMix {
    volume: number;
    pan: number;
    mute: boolean;
    solo: boolean;
    fade_in?: number;
    fade_out?: number;
    equalizer?: { low: number; mid: number; high: number };
    audio_effects?: unknown[];
    duck_others?: boolean;
}

export interface AudioMixCreateResponse {
    success: boolean;
    audio_mix_id: string;
}

export interface ChromaKey {
    enabled: boolean;
    key_color: string;
    similarity: number;
    smoothness?: number;
    spill_suppression?: number;
    background_type?: string;
    background_value?: string | null;
}

export interface ChromaKeyCreateResponse {
    success: boolean;
    chroma_key_id: string;
}

export interface Effect {
    id: string;
    effect_type: string;
    parameters: Record<string, unknown>;
    start_time: number;
    end_time: number;
    enabled: boolean;
}

export interface EffectsResponse {
    effects: Effect[];
}

export interface EffectCreateResponse {
    success: boolean;
    effect_id: string;
}

export interface SuccessResponse {
    success: boolean;
}

// ==================== Service ====================

export const videoEditorService = {
    // Projects
    async createProject(data: {
        title?: string;
        description?: string;
    }): Promise<ProjectResponse> {
        const formData = new FormData();
        if (data.title) formData.append('title', data.title);
        if (data.description) formData.append('description', data.description);
        return apiClient<ProjectResponse>('/api/editor/projects', {
            method: 'POST',
            body: formData,
            headers: {},
        });
    },

    async getUserProjects(params?: {
        status?: string;
        limit?: number;
    }): Promise<ProjectsResponse> {
        const searchParams = new URLSearchParams();
        if (params?.status) searchParams.set('status', params.status);
        if (params?.limit) searchParams.set('limit', params.limit.toString());
        const query = searchParams.toString();
        return apiClient<ProjectsResponse>(`/api/editor/projects${query ? `?${query}` : ''}`);
    },

    async getProject(projectId: string): Promise<ProjectResponse> {
        return apiClient<ProjectResponse>(`/api/editor/projects/${projectId}`);
    },

    async updateProjectTitle(projectId: string, title: string): Promise<ProjectResponse> {
        const formData = new FormData();
        formData.append('title', title);
        return apiClient<ProjectResponse>(`/api/editor/projects/${projectId}/title`, {
            method: 'PUT',
            body: formData,
            headers: {},
        });
    },

    async deleteProject(projectId: string): Promise<SuccessResponse> {
        return apiClient<SuccessResponse>(`/api/editor/projects/${projectId}`, {
            method: 'DELETE',
        });
    },

    // Assets
    async uploadAsset(projectId: string, file: File, assetType: string): Promise<AssetResponse> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('asset_type', assetType);
        return apiClient<AssetResponse>(`/api/editor/projects/${projectId}/assets`, {
            method: 'POST',
            body: formData,
            headers: {},
        });
    },

    async getProjectAssets(projectId: string, assetType?: string): Promise<AssetsResponse> {
        const params = assetType ? `?asset_type=${encodeURIComponent(assetType)}` : '';
        return apiClient<AssetsResponse>(`/api/editor/projects/${projectId}/assets${params}`);
    },

    async deleteAsset(assetId: string): Promise<SuccessResponse> {
        return apiClient<SuccessResponse>(`/api/editor/assets/${assetId}`, {
            method: 'DELETE',
        });
    },

    // Transitions
    async addTransition(projectId: string, data: {
        transition_type: string;
        start_time: number;
        end_time: number;
        duration: number;
        parameters?: string;
    }): Promise<TransitionResponse> {
        const formData = new FormData();
        formData.append('transition_type', data.transition_type);
        formData.append('start_time', data.start_time.toString());
        formData.append('end_time', data.end_time.toString());
        formData.append('duration', data.duration.toString());
        if (data.parameters) formData.append('parameters', data.parameters);
        return apiClient<TransitionResponse>(`/api/editor/projects/${projectId}/transitions`, {
            method: 'POST',
            body: formData,
            headers: {},
        });
    },

    async getProjectTransitions(projectId: string): Promise<TransitionsResponse> {
        return apiClient<TransitionsResponse>(`/api/editor/projects/${projectId}/transitions`);
    },

    // Tracks
    async addTrack(projectId: string, data: {
        asset_id: string;
        track_type: string;
        start_time: number;
        end_time: number;
    }): Promise<TrackResponse> {
        const formData = new FormData();
        formData.append('asset_id', data.asset_id);
        formData.append('track_type', data.track_type);
        formData.append('start_time', data.start_time.toString());
        formData.append('end_time', data.end_time.toString());
        return apiClient<TrackResponse>(`/api/editor/projects/${projectId}/tracks`, {
            method: 'POST',
            body: formData,
            headers: {},
        });
    },

    async getProjectTracks(projectId: string): Promise<TracksResponse> {
        return apiClient<TracksResponse>(`/api/editor/projects/${projectId}/tracks`);
    },

    // Captions
    async addCaption(projectId: string, data: {
        video_asset_id: string;
        text: string;
        start_time: number;
        end_time: number;
    }): Promise<CaptionResponse> {
        const formData = new FormData();
        formData.append('video_asset_id', data.video_asset_id);
        formData.append('text', data.text);
        formData.append('start_time', data.start_time.toString());
        formData.append('end_time', data.end_time.toString());
        return apiClient<CaptionResponse>(`/api/editor/projects/${projectId}/captions`, {
            method: 'POST',
            body: formData,
            headers: {},
        });
    },

    async getProjectCaptions(projectId: string, videoAssetId: string): Promise<CaptionsResponse> {
        return apiClient<CaptionsResponse>(`/api/editor/projects/${projectId}/videos/${videoAssetId}/captions`);
    },

    async deleteCaption(captionId: string): Promise<SuccessResponse> {
        return apiClient<SuccessResponse>(`/api/editor/captions/${captionId}`, {
            method: 'DELETE',
        });
    },

    // Monetization
    async getMonetizationSettings(projectId: string): Promise<MonetizationSettings> {
        return apiClient<MonetizationSettings>(`/api/editor/projects/${projectId}/monetization`);
    },

    async updateMonetizationSettings(projectId: string, data: {
        tips_enabled?: boolean;
        subscriptions_enabled?: boolean;
        suggested_tip_amounts?: number[];
        subscription_price?: number;
        subscription_tier_name?: string;
    }): Promise<MonetizationUpdateResponse> {
        return apiClient<MonetizationUpdateResponse>(`/api/editor/projects/${projectId}/monetization`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    // Publish / Export
    async publishProject(projectId: string, data?: {
        visibility?: string;
    }): Promise<PublishResponse> {
        return apiClient<PublishResponse>(`/api/editor/projects/${projectId}/publish`, {
            method: 'POST',
            body: JSON.stringify(data || {}),
        });
    },

    async exportProject(projectId: string, data?: {
        format?: string;
        quality?: string;
    }): Promise<ExportResponse> {
        return apiClient<ExportResponse>(`/api/editor/projects/${projectId}/export`, {
            method: 'POST',
            body: JSON.stringify(data || {}),
        });
    },

    async getExportStatus(projectId: string): Promise<ExportStatusResponse> {
        return apiClient<ExportStatusResponse>(`/api/editor/projects/${projectId}/export-status`);
    },

    async duplicateProject(projectId: string): Promise<DuplicateResponse> {
        return apiClient<DuplicateResponse>(`/api/editor/projects/${projectId}/duplicate`, {
            method: 'POST',
        });
    },

    // Keyframes
    async addKeyframe(projectId: string, trackId: string, data: {
        property_name: string;
        time: number;
        value: unknown;
        easing?: string;
    }): Promise<KeyframeCreateResponse> {
        return apiClient<KeyframeCreateResponse>(`/api/editor/projects/${projectId}/tracks/${trackId}/keyframes`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getKeyframes(projectId: string, trackId: string): Promise<KeyframesResponse> {
        return apiClient<KeyframesResponse>(`/api/editor/projects/${projectId}/tracks/${trackId}/keyframes`);
    },

    async deleteKeyframe(keyframeId: string): Promise<SuccessResponse> {
        return apiClient<SuccessResponse>(`/api/editor/keyframes/${keyframeId}`, {
            method: 'DELETE',
        });
    },

    // Color Grading
    async setColorGrade(projectId: string, trackId: string, data: {
        brightness?: number;
        contrast?: number;
        saturation?: number;
        temperature?: number;
        tint?: number;
        highlights?: number;
        shadows?: number;
        vibrance?: number;
        filters?: string[];
    }): Promise<ColorGradeCreateResponse> {
        return apiClient<ColorGradeCreateResponse>(`/api/editor/projects/${projectId}/tracks/${trackId}/color-grade`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getColorGrade(projectId: string, trackId: string): Promise<ColorGrade> {
        return apiClient<ColorGrade>(`/api/editor/projects/${projectId}/tracks/${trackId}/color-grade`);
    },

    // Audio Mixing
    async setAudioMix(projectId: string, trackId: string, data: {
        volume?: number;
        pan?: number;
        mute?: boolean;
        solo?: boolean;
        fade_in?: number;
        fade_out?: number;
        equalizer?: { low: number; mid: number; high: number };
        audio_effects?: unknown[];
        duck_others?: boolean;
    }): Promise<AudioMixCreateResponse> {
        return apiClient<AudioMixCreateResponse>(`/api/editor/projects/${projectId}/tracks/${trackId}/audio-mix`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getAudioMix(projectId: string, trackId: string): Promise<AudioMix> {
        return apiClient<AudioMix>(`/api/editor/projects/${projectId}/tracks/${trackId}/audio-mix`);
    },

    // Chroma Key
    async setChromaKey(projectId: string, trackId: string, data: {
        enabled?: boolean;
        key_color?: string;
        similarity?: number;
        smoothness?: number;
        spill_suppression?: number;
        background_type?: string;
        background_value?: string;
    }): Promise<ChromaKeyCreateResponse> {
        return apiClient<ChromaKeyCreateResponse>(`/api/editor/projects/${projectId}/tracks/${trackId}/chroma-key`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getChromaKey(projectId: string, trackId: string): Promise<ChromaKey> {
        return apiClient<ChromaKey>(`/api/editor/projects/${projectId}/tracks/${trackId}/chroma-key`);
    },

    // Effects
    async addEffect(projectId: string, trackId: string, data: {
        effect_type: string;
        parameters?: Record<string, unknown>;
        start_time?: number;
        end_time?: number;
        enabled?: boolean;
    }): Promise<EffectCreateResponse> {
        return apiClient<EffectCreateResponse>(`/api/editor/projects/${projectId}/tracks/${trackId}/effects`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getEffects(projectId: string, trackId: string): Promise<EffectsResponse> {
        return apiClient<EffectsResponse>(`/api/editor/projects/${projectId}/tracks/${trackId}/effects`);
    },

    async deleteEffect(effectId: string): Promise<SuccessResponse> {
        return apiClient<SuccessResponse>(`/api/editor/effects/${effectId}`, {
            method: 'DELETE',
        });
    },
};
