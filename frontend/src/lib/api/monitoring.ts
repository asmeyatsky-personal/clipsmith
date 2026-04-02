import { apiClient } from './client';

// ==================== Response Types ====================

export interface HealthStatus {
    status: string;
    environment: string;
    version: string;
    service: string;
    error?: string;
    [key: string]: unknown;
}

export interface APIRequest {
    endpoint: string;
    timestamp: string;
    response_time: number;
    status_code: number;
    [key: string]: unknown;
}

export interface TimePeriodStats {
    days: number;
    requests_count: number;
    average_response_time: number;
    error_rate: number;
}

export interface MetricsSummary {
    api_requests: APIRequest[];
    time_period_stats?: TimePeriodStats;
    [key: string]: unknown;
}

export interface LogsResponse {
    lines: string[];
    level: string;
    total_lines: number;
    lines_returned: number;
    error?: string;
}

export interface TestLogResponse {
    message: string;
    timestamp: string | null;
}

export interface EndpointPerformance {
    requests: number;
    total_response_time: number;
    errors: number;
    avg_response_time: number;
}

export interface PerformanceMetrics {
    summary: MetricsSummary;
    endpoint_performance: Record<string, EndpointPerformance>;
    overall_average_response_time: number;
    hours_analyzed: number;
}

// ==================== Service ====================

export const monitoringService = {
    async getHealth(): Promise<HealthStatus> {
        return apiClient<HealthStatus>('/monitoring/health');
    },

    async getMetrics(days?: number): Promise<MetricsSummary> {
        const params = days ? `?days=${days}` : '';
        return apiClient<MetricsSummary>(`/monitoring/metrics${params}`);
    },

    async getLogs(params?: {
        lines?: number;
        level?: string;
    }): Promise<LogsResponse> {
        const searchParams = new URLSearchParams();
        if (params?.lines) searchParams.set('lines', params.lines.toString());
        if (params?.level) searchParams.set('level', params.level);
        const query = searchParams.toString();
        return apiClient<LogsResponse>(`/monitoring/logs${query ? `?${query}` : ''}`);
    },

    async testLog(message?: string): Promise<TestLogResponse> {
        const params = message ? `?message=${encodeURIComponent(message)}` : '';
        return apiClient<TestLogResponse>(`/monitoring/test-log${params}`, {
            method: 'POST',
        });
    },

    async getPerformance(hours?: number): Promise<PerformanceMetrics> {
        const params = hours ? `?hours=${hours}` : '';
        return apiClient<PerformanceMetrics>(`/monitoring/performance${params}`);
    },
};
