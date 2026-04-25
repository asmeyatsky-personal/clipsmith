'use client';

import { Capacitor } from '@capacitor/core';
import { PushNotifications, Token } from '@capacitor/push-notifications';
import { apiClient } from '@/lib/api/client';

let initialized = false;

/**
 * Request push permission and register the device token with the backend.
 * Call after a user is authenticated.
 *
 * Web/PWA: noop. iOS/Android: requests permission, registers, sends token
 * to POST /push/register.
 */
export async function initPushNotifications(): Promise<void> {
    if (initialized) return;
    if (!Capacitor.isNativePlatform()) return;

    initialized = true;

    try {
        const perm = await PushNotifications.checkPermissions();
        let granted = perm.receive === 'granted';
        if (!granted) {
            const requested = await PushNotifications.requestPermissions();
            granted = requested.receive === 'granted';
        }
        if (!granted) {
            console.info('[push] permission denied');
            return;
        }

        await PushNotifications.register();

        PushNotifications.addListener('registration', async (token: Token) => {
            try {
                await apiClient('/push/register', {
                    method: 'POST',
                    body: JSON.stringify({
                        token: token.value,
                        platform: Capacitor.getPlatform(), // 'ios' | 'android' | 'web'
                    }),
                });
                console.info('[push] token registered');
            } catch (e) {
                console.warn('[push] failed to register token', e);
            }
        });

        PushNotifications.addListener('registrationError', (err) => {
            console.warn('[push] registration error', err);
        });

        PushNotifications.addListener('pushNotificationReceived', (notification) => {
            console.info('[push] received', notification);
        });

        PushNotifications.addListener('pushNotificationActionPerformed', (action) => {
            // Routing on tap: action.notification.data may include {videoId, profileId, ...}
            const data = (action.notification.data ?? {}) as Record<string, string>;
            if (typeof window !== 'undefined') {
                if (data.videoId) {
                    window.location.href = `/feed?v=${encodeURIComponent(data.videoId)}`;
                } else if (data.profileId) {
                    window.location.href = `/profile?u=${encodeURIComponent(data.profileId)}`;
                }
            }
        });
    } catch (e) {
        console.warn('[push] initialization failed', e);
    }
}
