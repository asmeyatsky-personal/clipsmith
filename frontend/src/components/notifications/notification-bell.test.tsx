import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { NotificationBell } from './notification-bell';

vi.mock('@/lib/api/notification', () => ({
    notificationService: {
        getUnreadCount: vi.fn().mockResolvedValue({ unread_count: 3 }),
        getNotifications: vi.fn().mockResolvedValue([]),
        markAsRead: vi.fn().mockResolvedValue({}),
        markAllAsRead: vi.fn().mockResolvedValue({}),
    },
}));

describe('NotificationBell', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders the bell button', () => {
        render(<NotificationBell />);
        expect(screen.getByRole('button', { name: /notifications/i })).toBeInTheDocument();
    });

    it('shows unread count badge after fetch', async () => {
        render(<NotificationBell />);
        // Wait for the async useEffect to populate
        const badge = await screen.findByText('3');
        expect(badge).toBeInTheDocument();
    });
});
