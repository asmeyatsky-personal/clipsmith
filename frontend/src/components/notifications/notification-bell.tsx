'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Bell, X } from 'lucide-react';
import { notificationService, Notification } from '@/lib/api/notification';

const REFRESH_MS = 30_000;

export function NotificationBell() {
    const [open, setOpen] = useState(false);
    const [unread, setUnread] = useState(0);
    const [items, setItems] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(false);

    const refresh = async () => {
        try {
            const c = await notificationService.getUnreadCount();
            setUnread(c.unread_count ?? 0);
        } catch {
            // unauth or net err — silent
        }
    };

    useEffect(() => {
        refresh();
        const t = setInterval(refresh, REFRESH_MS);
        return () => clearInterval(t);
    }, []);

    const openDrawer = async () => {
        setOpen(true);
        setLoading(true);
        try {
            const list = await notificationService.getNotifications({ limit: 30 });
            setItems(list as unknown as Notification[]);
        } catch {
            // silent
        } finally {
            setLoading(false);
        }
    };

    const markAll = async () => {
        try {
            await notificationService.markAllAsRead();
            setItems((cur) => cur.map((n) => ({ ...n, status: 'read' })));
            setUnread(0);
        } catch {}
    };

    const handleItemClick = async (n: Notification) => {
        try {
            await notificationService.markAsRead(n.id);
        } catch {}
        // best-effort routing — types are defined by server
        const data = (n.data as Record<string, string> | undefined) ?? {};
        if (data.video_id) window.location.href = `/feed?v=${encodeURIComponent(data.video_id)}`;
        else if (data.user_id) window.location.href = `/profile?u=${encodeURIComponent(data.user_id)}`;
        setOpen(false);
    };

    return (
        <>
            <button
                onClick={openDrawer}
                className="pointer-events-auto relative bg-black/30 backdrop-blur rounded-full p-2"
                aria-label="Notifications"
            >
                <Bell className="w-5 h-5 text-white" />
                {unread > 0 && (
                    <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-red-500 text-[10px] font-bold flex items-center justify-center">
                        {unread > 99 ? '99+' : unread}
                    </span>
                )}
            </button>

            {open && (
                <div className="fixed inset-0 z-50 flex items-end sm:items-center sm:justify-end" role="dialog">
                    <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />
                    <div className="relative w-full sm:max-w-sm sm:m-4 bg-zinc-900 text-white rounded-t-2xl sm:rounded-2xl max-h-[80vh] flex flex-col">
                        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
                            <h3 className="font-semibold">Notifications</h3>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={markAll}
                                    className="text-xs text-zinc-400 hover:text-white"
                                >
                                    Mark all read
                                </button>
                                <button onClick={() => setOpen(false)} aria-label="Close">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                        <div className="flex-1 overflow-y-auto">
                            {loading && <p className="p-4 text-sm text-zinc-500">Loading…</p>}
                            {!loading && items.length === 0 && (
                                <p className="p-8 text-sm text-zinc-500 text-center">No notifications yet</p>
                            )}
                            {items.map((n) => (
                                <button
                                    key={n.id}
                                    onClick={() => handleItemClick(n)}
                                    className={`w-full text-left px-4 py-3 border-b border-zinc-800 hover:bg-zinc-800/50 ${
                                        n.status === 'unread' ? 'bg-blue-500/5' : ''
                                    }`}
                                >
                                    <div className="font-medium text-sm">{n.title}</div>
                                    <div className="text-xs text-zinc-400">{n.message}</div>
                                    {n.created_at && (
                                        <div className="text-[10px] text-zinc-600 mt-1">
                                            {new Date(n.created_at).toLocaleString()}
                                        </div>
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
