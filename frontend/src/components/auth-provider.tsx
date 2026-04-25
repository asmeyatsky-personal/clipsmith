'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/lib/auth/auth-store';
import { initPushNotifications } from '@/lib/native/push';

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const { fetchCurrentUser, isLoading, user } = useAuthStore();

    useEffect(() => {
        fetchCurrentUser();
    }, [fetchCurrentUser]);

    useEffect(() => {
        if (user) {
            // Fire-and-forget — won't block render. Noop on web/PWA.
            initPushNotifications();
        }
    }, [user]);

    if (isLoading) {
        return null;
    }

    return <>{children}</>;
}
