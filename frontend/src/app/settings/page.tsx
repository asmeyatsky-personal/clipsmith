'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
    ArrowLeft,
    LogOut,
    Trash2,
    Download,
    Shield,
    FileText,
    AlertTriangle,
    Loader2,
} from 'lucide-react';
import { useAuthStore } from '@/lib/auth/auth-store';
import { complianceService } from '@/lib/api/compliance';

export default function SettingsPage() {
    const router = useRouter();
    const { user, logout } = useAuthStore();
    const [busy, setBusy] = useState<'export' | 'delete' | null>(null);
    const [confirmDelete, setConfirmDelete] = useState(false);
    const [confirmText, setConfirmText] = useState('');
    const [error, setError] = useState<string | null>(null);

    const handleLogout = async () => {
        await logout();
        router.push('/login');
    };

    const handleExport = async () => {
        setBusy('export');
        setError(null);
        try {
            const r = await complianceService.exportUserData();
            alert(
                `Export request submitted (id: ${r.request_id}). You'll receive an email when it's ready (usually within 30 days, GDPR Art. 12).`,
            );
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Export request failed');
        } finally {
            setBusy(null);
        }
    };

    const handleDelete = async () => {
        if (confirmText !== 'DELETE') {
            setError('Type DELETE to confirm');
            return;
        }
        setBusy('delete');
        setError(null);
        try {
            await complianceService.deleteUserData({ categories: ['all'] });
            alert(
                'Your account deletion request was submitted. You will be logged out now. We process deletions within 30 days (GDPR Art. 17).',
            );
            await logout();
            router.push('/login');
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Deletion request failed');
        } finally {
            setBusy(null);
        }
    };

    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-white">
                <Link href="/login" className="underline">
                    Log in to manage your account
                </Link>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-950 text-white">
            <div className="flex items-center gap-3 px-4 pt-[max(env(safe-area-inset-top),12px)] pb-3 border-b border-zinc-800">
                <button onClick={() => router.back()} aria-label="Back">
                    <ArrowLeft className="w-6 h-6" />
                </button>
                <h1 className="font-semibold">Settings</h1>
            </div>

            <div className="max-w-md mx-auto p-4 pb-[max(env(safe-area-inset-bottom),32px)] space-y-6">
                <section>
                    <div className="text-xs uppercase tracking-wider text-zinc-500 mb-2">
                        Account
                    </div>
                    <div className="rounded-xl bg-zinc-900 divide-y divide-zinc-800">
                        <div className="px-4 py-3">
                            <div className="text-xs text-zinc-500">Username</div>
                            <div className="font-mono">@{user.username}</div>
                        </div>
                        <div className="px-4 py-3">
                            <div className="text-xs text-zinc-500">Email</div>
                            <div>{user.email}</div>
                        </div>
                    </div>
                </section>

                <section>
                    <div className="text-xs uppercase tracking-wider text-zinc-500 mb-2">
                        Privacy & Data
                    </div>
                    <div className="rounded-xl bg-zinc-900 divide-y divide-zinc-800">
                        <button
                            onClick={handleExport}
                            disabled={busy === 'export'}
                            className="w-full px-4 py-3 flex items-center gap-3 hover:bg-zinc-800/50 disabled:opacity-50 text-left"
                        >
                            {busy === 'export' ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Download className="w-5 h-5" />
                            )}
                            <div>
                                <div className="font-medium">Export my data</div>
                                <div className="text-xs text-zinc-500">
                                    GDPR Art. 20 portable export
                                </div>
                            </div>
                        </button>
                        <Link
                            href="/legal/privacy"
                            className="w-full px-4 py-3 flex items-center gap-3 hover:bg-zinc-800/50"
                        >
                            <Shield className="w-5 h-5" />
                            <span className="font-medium">Privacy Policy</span>
                        </Link>
                        <Link
                            href="/legal/terms"
                            className="w-full px-4 py-3 flex items-center gap-3 hover:bg-zinc-800/50"
                        >
                            <FileText className="w-5 h-5" />
                            <span className="font-medium">Terms of Service</span>
                        </Link>
                    </div>
                </section>

                <section>
                    <div className="text-xs uppercase tracking-wider text-zinc-500 mb-2">
                        Session
                    </div>
                    <button
                        onClick={handleLogout}
                        className="w-full rounded-xl bg-zinc-900 px-4 py-3 flex items-center gap-3 hover:bg-zinc-800/50"
                    >
                        <LogOut className="w-5 h-5" />
                        <span className="font-medium">Log out</span>
                    </button>
                </section>

                {/* Danger zone — required by Apple Guideline 5.1.1(v) */}
                <section>
                    <div className="text-xs uppercase tracking-wider text-red-500 mb-2">
                        Danger zone
                    </div>
                    {!confirmDelete ? (
                        <button
                            onClick={() => setConfirmDelete(true)}
                            className="w-full rounded-xl border border-red-900 bg-red-950/30 px-4 py-3 flex items-center gap-3 text-red-400 hover:bg-red-950/50"
                        >
                            <Trash2 className="w-5 h-5" />
                            <div className="text-left">
                                <div className="font-medium">Delete my account</div>
                                <div className="text-xs text-red-400/70">
                                    Permanently remove all data (GDPR Art. 17)
                                </div>
                            </div>
                        </button>
                    ) : (
                        <div className="rounded-xl border border-red-900 bg-red-950/30 p-4 space-y-3">
                            <div className="flex items-center gap-2 text-red-400">
                                <AlertTriangle className="w-5 h-5" />
                                <span className="font-semibold">This cannot be undone</span>
                            </div>
                            <p className="text-sm text-red-200/80">
                                All your videos, comments, follows, and profile data will be
                                permanently deleted. To confirm, type <code className="px-1 bg-red-950 rounded">DELETE</code> below.
                            </p>
                            <input
                                type="text"
                                value={confirmText}
                                onChange={(e) => setConfirmText(e.target.value)}
                                placeholder="DELETE"
                                className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-white"
                            />
                            <div className="flex gap-2">
                                <button
                                    onClick={() => {
                                        setConfirmDelete(false);
                                        setConfirmText('');
                                        setError(null);
                                    }}
                                    className="flex-1 px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleDelete}
                                    disabled={busy === 'delete' || confirmText !== 'DELETE'}
                                    className="flex-1 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 disabled:opacity-50 flex items-center justify-center gap-2"
                                >
                                    {busy === 'delete' && <Loader2 className="w-4 h-4 animate-spin" />}
                                    Delete forever
                                </button>
                            </div>
                        </div>
                    )}
                </section>

                {error && (
                    <p className="text-sm text-red-400 text-center">{error}</p>
                )}
            </div>
        </div>
    );
}
