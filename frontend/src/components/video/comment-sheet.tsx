'use client';

import { useEffect, useState } from 'react';
import { X, Send } from 'lucide-react';
import { interactionService, type Comment } from '@/lib/api/interactions';
import { useAuthStore } from '@/lib/auth/auth-store';

interface CommentSheetProps {
    videoId: string;
    onClose: () => void;
}

export function CommentSheet({ videoId, onClose }: CommentSheetProps) {
    const { user } = useAuthStore();
    const [comments, setComments] = useState<Comment[]>([]);
    const [loading, setLoading] = useState(true);
    const [text, setText] = useState('');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            setLoading(true);
            try {
                const list = await interactionService.listComments(videoId);
                if (!cancelled) setComments(list);
            } catch {
                // silent
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => {
            cancelled = true;
        };
    }, [videoId]);

    const submit = async () => {
        const value = text.trim();
        if (!value || !user) return;
        setSubmitting(true);
        try {
            const created = await interactionService.addComment(videoId, value);
            setComments((c) => [created, ...c]);
            setText('');
        } catch {
            // silent
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-end" role="dialog">
            <div
                className="absolute inset-0 bg-black/50"
                onClick={onClose}
                aria-label="Close comments"
            />
            <div className="relative w-full bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white rounded-t-2xl max-h-[75vh] flex flex-col pb-[max(env(safe-area-inset-bottom),16px)]">
                <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-200 dark:border-zinc-800">
                    <h3 className="font-semibold">Comments</h3>
                    <button onClick={onClose} aria-label="Close">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
                    {loading && <p className="text-sm text-zinc-500">Loading…</p>}
                    {!loading && comments.length === 0 && (
                        <p className="text-sm text-zinc-500 text-center py-8">
                            No comments yet. Be the first.
                        </p>
                    )}
                    {comments.map((c) => (
                        <div key={c.id} className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-zinc-300 dark:bg-zinc-700 flex-shrink-0" />
                            <div className="flex-1">
                                <div className="font-semibold text-sm">{c.username}</div>
                                <div className="text-sm">{c.content}</div>
                            </div>
                        </div>
                    ))}
                </div>

                {user ? (
                    <form
                        className="flex gap-2 p-3 border-t border-zinc-200 dark:border-zinc-800"
                        onSubmit={(e) => {
                            e.preventDefault();
                            submit();
                        }}
                    >
                        <input
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                            placeholder="Add a comment…"
                            maxLength={500}
                            className="flex-1 px-3 py-2 rounded-full bg-zinc-100 dark:bg-zinc-800 text-sm focus:outline-none"
                        />
                        <button
                            type="submit"
                            disabled={!text.trim() || submitting}
                            className="px-3 rounded-full bg-blue-500 text-white disabled:opacity-50"
                            aria-label="Send comment"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </form>
                ) : (
                    <p className="text-sm text-zinc-500 text-center p-3 border-t border-zinc-200 dark:border-zinc-800">
                        Log in to comment
                    </p>
                )}
            </div>
        </div>
    );
}
