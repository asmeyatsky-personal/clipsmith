import { apiClient } from './client';

// ==================== Response Types ====================

export interface Notification {
    id: string;
    user_id: string;
    type: string;
    title: string;
    message: string;
    status: string;
    created_at: string | null;
    read_at: string | null;
    [key: string]: unknown;
}

export interface NotificationSummary {
    unread_count: number;
    total_count: number;
    recent: Notification[];
    [key: string]: unknown;
}

export interface MarkReadResponse {
    message: string;
    success: boolean;
}

export interface MarkAllReadResponse {
    message: string;
    count: number;
}

export interface UnreadCountResponse {
    unread_count: number;
}

export interface DeleteNotificationResponse {
    message: string;
    success: boolean;
}

// ==================== Service ====================

export const notificationService = {
    async getNotifications(params?: {
        status?: 'unread' | 'read' | 'archived';
        offset?: number;
        limit?: number;
    }): Promise<Notification[]> {
        const searchParams = new URLSearchParams();
        if (params?.status) searchParams.set('status', params.status);
        if (params?.offset !== undefined) searchParams.set('offset', params.offset.toString());
        if (params?.limit) searchParams.set('limit', params.limit.toString());
        const query = searchParams.toString();
        return apiClient<Notification[]>(`/notifications/${query ? `?${query}` : ''}`);
    },

    async getSummary(): Promise<NotificationSummary> {
        return apiClient<NotificationSummary>('/notifications/summary');
    },

    async markAsRead(notificationId: string): Promise<MarkReadResponse> {
        return apiClient<MarkReadResponse>(`/notifications/${notificationId}/read`, {
            method: 'POST',
        });
    },

    async markAllAsRead(): Promise<MarkAllReadResponse> {
        return apiClient<MarkAllReadResponse>('/notifications/mark-all-read', {
            method: 'POST',
        });
    },

    async getUnreadCount(): Promise<UnreadCountResponse> {
        return apiClient<UnreadCountResponse>('/notifications/unread-count');
    },

    async deleteNotification(notificationId: string): Promise<DeleteNotificationResponse> {
        return apiClient<DeleteNotificationResponse>(`/notifications/${notificationId}`, {
            method: 'DELETE',
        });
    },
};
