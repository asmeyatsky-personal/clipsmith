import { apiClient } from './client';

// ==================== Response Types ====================

export interface GDPRRequest {
    id: string;
    request_type: string;
    status: string;
    submitted_at: string | null;
    completed_at?: string | null;
}

export interface GDPRRequestResponse {
    success: boolean;
    request: GDPRRequest;
}

export interface GDPRExportResponse {
    success: boolean;
    message: string;
    request_id: string;
}

export interface GDPRDeleteResponse {
    success: boolean;
    message: string;
    request_id: string;
}

export interface ConsentRecord {
    id: string;
    consent_type: string;
    granted: boolean;
    updated_at: string | null;
}

export interface ConsentResponse {
    success: boolean;
    consent_type: string;
    granted: boolean;
}

export interface ConsentsListResponse {
    success: boolean;
    consents: ConsentRecord[];
}

export interface ConsentWithdrawResponse {
    success: boolean;
    message: string;
}

export interface AgeVerificationResponse {
    success: boolean;
    age: number;
    is_minor: boolean;
    requires_parental_consent: boolean;
    status: string;
    message?: string;
}

export interface CCPADataResponse {
    success: boolean;
    user_id: string;
    data_categories_collected: string[];
    data_shared_with_third_parties: boolean;
    opt_out_status: boolean;
    message: string;
}

export interface CCPAOptOutResponse {
    success: boolean;
    message: string;
    opt_out_effective: boolean;
}

// ==================== Service ====================

export const complianceService = {
    // GDPR
    async submitGDPRRequest(data: {
        request_type: 'export' | 'deletion' | 'rectification' | 'restriction' | 'portability';
    }): Promise<GDPRRequestResponse> {
        return apiClient<GDPRRequestResponse>('/api/compliance/gdpr/request', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getGDPRRequestStatus(requestId: string): Promise<GDPRRequestResponse> {
        return apiClient<GDPRRequestResponse>(`/api/compliance/gdpr/request/${requestId}`);
    },

    async exportUserData(): Promise<GDPRExportResponse> {
        return apiClient<GDPRExportResponse>('/api/compliance/gdpr/export', {
            method: 'POST',
        });
    },

    async deleteUserData(data: {
        categories: ('profile' | 'videos' | 'comments' | 'likes' | 'messages' | 'analytics' | 'all')[];
    }): Promise<GDPRDeleteResponse> {
        return apiClient<GDPRDeleteResponse>('/api/compliance/gdpr/delete', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // Consent
    async recordConsent(data: {
        consent_type: 'analytics' | 'marketing' | 'personalization' | 'third_party' | 'cookies';
        granted: boolean;
    }): Promise<ConsentResponse> {
        return apiClient<ConsentResponse>('/api/compliance/consent', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getUserConsents(): Promise<ConsentsListResponse> {
        return apiClient<ConsentsListResponse>('/api/compliance/consent');
    },

    async withdrawConsent(data: {
        consent_type: string;
    }): Promise<ConsentWithdrawResponse> {
        return apiClient<ConsentWithdrawResponse>('/api/compliance/consent/withdraw', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // Age Verification
    async verifyAge(data: {
        date_of_birth: string;
    }): Promise<AgeVerificationResponse> {
        return apiClient<AgeVerificationResponse>('/api/compliance/age-verification', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // CCPA
    async getCCPAData(): Promise<CCPADataResponse> {
        return apiClient<CCPADataResponse>('/api/compliance/ccpa/data');
    },

    async optOutDataSale(): Promise<CCPAOptOutResponse> {
        return apiClient<CCPAOptOutResponse>('/api/compliance/ccpa/opt-out', {
            method: 'POST',
        });
    },
};
