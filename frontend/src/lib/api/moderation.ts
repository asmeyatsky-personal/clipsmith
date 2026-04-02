import { apiClient } from './client';

// ==================== Response Types ====================

export interface ModerationItem {
    id: string;
    content_type: string;
    content_id: string;
    user_id: string;
    status: string;
    severity: string | null;
    reason: string | null;
    confidence_score: number | null;
    ai_labels: string[] | null;
    auto_action: string | null;
    created_at: string;
    reviewed_at: string | null;
    completed_at: string | null;
    human_reviewer_id: string | null;
    human_notes: string | null;
}

export interface ModerationQueueResponse {
    moderations: ModerationItem[];
    total: number;
    filters: {
        status: string | null;
        severity: string | null;
    };
}

export interface ModerationReviewResponse {
    message: string;
    moderation: {
        id: string;
        status: string;
    };
}

export interface BulkModerationResponse {
    message: string;
    processed_count: number;
    error_count: number;
    errors: string[];
}

export interface ModerationStatistics {
    period_days: number;
    total_moderated: number;
    approved: number;
    rejected: number;
    flagged: number;
    high_severity: number;
    critical_severity: number;
    approval_rate: number;
    rejection_rate: number;
}

export interface ReviewerStatistics {
    reviewer_id: string;
    total_reviewed: number;
    approved: number;
    rejected: number;
    average_review_time: number;
    [key: string]: unknown;
}

export interface CleanupResponse {
    message: string;
    deleted_count: number;
    days_threshold: number;
}

// ==================== Service ====================

export const moderationService = {
    async getQueue(params?: {
        status?: string;
        severity?: string;
        limit?: number;
    }): Promise<ModerationQueueResponse> {
        const searchParams = new URLSearchParams();
        if (params?.status) searchParams.set('status', params.status);
        if (params?.severity) searchParams.set('severity', params.severity);
        if (params?.limit) searchParams.set('limit', params.limit.toString());
        const query = searchParams.toString();
        return apiClient<ModerationQueueResponse>(`/moderation/queue${query ? `?${query}` : ''}`);
    },

    async reviewContent(moderationId: string, data: {
        moderation_id: string;
        action: 'approve' | 'reject';
        reason?: string;
        severity?: string;
        notes?: string;
    }): Promise<ModerationReviewResponse> {
        return apiClient<ModerationReviewResponse>(`/moderation/review/${moderationId}`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async bulkReview(data: {
        moderation_ids: string[];
        action: 'approve' | 'reject';
        notes?: string;
    }): Promise<BulkModerationResponse> {
        return apiClient<BulkModerationResponse>('/moderation/bulk-review', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getStatistics(days?: number): Promise<ModerationStatistics> {
        const params = days ? `?days=${days}` : '';
        return apiClient<ModerationStatistics>(`/moderation/statistics${params}`);
    },

    async getReviewerStatistics(reviewerId: string, days?: number): Promise<ReviewerStatistics> {
        const params = days ? `?days=${days}` : '';
        return apiClient<ReviewerStatistics>(`/moderation/reviewer-stats/${reviewerId}${params}`);
    },

    async cleanupOldRecords(days?: number): Promise<CleanupResponse> {
        const params = days ? `?days=${days}` : '';
        return apiClient<CleanupResponse>(`/moderation/cleanup${params}`, {
            method: 'POST',
        });
    },
};
