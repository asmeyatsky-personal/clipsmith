import { apiClient } from './client';

// ==================== Response Types ====================

export interface SetupTwoFactorResponse {
    success: boolean;
    secret: string;
    qr_code: string;
    backup_codes: string[];
    message: string;
}

export interface VerifyTwoFactorResponse {
    success: boolean;
    message: string;
}

export interface DisableTwoFactorResponse {
    success: boolean;
    message: string;
}

export interface TwoFactorStatusResponse {
    success: boolean;
    enabled: boolean;
    method: string | null;
}

export interface BackupCodeVerifyResponse {
    success: boolean;
    message: string;
    remaining_codes: number;
}

// ==================== Service ====================

export const twoFactorService = {
    async setup(): Promise<SetupTwoFactorResponse> {
        return apiClient<SetupTwoFactorResponse>('/api/auth/2fa/setup', {
            method: 'POST',
        });
    },

    async verify(code: string): Promise<VerifyTwoFactorResponse> {
        return apiClient<VerifyTwoFactorResponse>('/api/auth/2fa/verify', {
            method: 'POST',
            body: JSON.stringify({ code }),
        });
    },

    async disable(code: string): Promise<DisableTwoFactorResponse> {
        return apiClient<DisableTwoFactorResponse>('/api/auth/2fa/disable', {
            method: 'POST',
            body: JSON.stringify({ code }),
        });
    },

    async getStatus(): Promise<TwoFactorStatusResponse> {
        return apiClient<TwoFactorStatusResponse>('/api/auth/2fa/status');
    },

    async verifyBackupCode(code: string): Promise<BackupCodeVerifyResponse> {
        return apiClient<BackupCodeVerifyResponse>('/api/auth/2fa/backup-codes/verify', {
            method: 'POST',
            body: JSON.stringify({ code }),
        });
    },
};
