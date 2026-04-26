'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { userService } from '@/lib/api/user';

interface UserSummary {
    id: string;
    username: string;
    bio?: string;
    avatar_url?: string | null;
}

function FollowersInner() {
    const router = useRouter();
    const params = useSearchParams();
    const userId = params.get('uid') ?? '';
    const mode = (params.get('mode') ?? 'followers') as 'followers' | 'following';
    const [items, setItems] = useState<UserSummary[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!userId) return;
        const fn = mode === 'following' ? userService.listFollowing : userService.listFollowers;
        fn(userId)
            .then((r) => setItems((r as { items: UserSummary[] }).items ?? []))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, [userId, mode]);

    return (
        <div className="min-h-screen bg-zinc-950 text-white">
            <div className="flex items-center gap-3 px-4 pt-[max(env(safe-area-inset-top),12px)] pb-3 border-b border-zinc-800">
                <button onClick={() => router.back()} aria-label="Back">
                    <ArrowLeft className="w-6 h-6" />
                </button>
                <h1 className="font-semibold capitalize">{mode}</h1>
            </div>

            <div className="max-w-md mx-auto">
                {loading && (
                    <div className="p-8 flex justify-center">
                        <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
                    </div>
                )}
                {!loading && items.length === 0 && (
                    <p className="p-8 text-center text-zinc-500">Nobody yet</p>
                )}
                {items.map((u) => (
                    <Link
                        key={u.id}
                        href={`/profile?u=${u.username}`}
                        className="flex items-center gap-3 px-4 py-3 hover:bg-zinc-900 border-b border-zinc-900"
                    >
                        <div className="w-10 h-10 rounded-full bg-zinc-800 overflow-hidden flex-shrink-0">
                            {u.avatar_url && (
                                <img src={u.avatar_url} alt="" className="w-full h-full object-cover" />
                            )}
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="font-semibold">@{u.username}</div>
                            {u.bio && (
                                <div className="text-xs text-zinc-500 truncate">{u.bio}</div>
                            )}
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
}

export default function FollowersPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-zinc-950" />}>
            <FollowersInner />
        </Suspense>
    );
}
