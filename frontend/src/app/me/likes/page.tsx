'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Heart, Loader2 } from 'lucide-react';
import { userService } from '@/lib/api/user';
import { useAuthStore } from '@/lib/auth/auth-store';

interface LikedVideo {
    id: string;
    title: string;
    thumbnail_url: string | null;
    creator_id: string;
    views: number;
    likes: number;
    duration: number;
}

export default function MyLikesPage() {
    const router = useRouter();
    const { user } = useAuthStore();
    const [items, setItems] = useState<LikedVideo[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!user) return;
        userService
            .listMyLikes()
            .then((r) => setItems(((r as { items: LikedVideo[] }).items ?? []) as LikedVideo[]))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, [user]);

    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-white">
                <Link href="/login" className="underline">
                    Log in to see your liked videos
                </Link>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-950 text-white pb-[max(env(safe-area-inset-bottom),16px)]">
            <div className="flex items-center gap-3 px-4 pt-[max(env(safe-area-inset-top),12px)] pb-3 border-b border-zinc-800">
                <button onClick={() => router.back()} aria-label="Back">
                    <ArrowLeft className="w-6 h-6" />
                </button>
                <Heart className="w-5 h-5 text-red-500 fill-red-500" />
                <h1 className="font-semibold">Liked videos</h1>
            </div>

            <div className="max-w-2xl mx-auto p-4">
                {loading && (
                    <div className="p-8 flex justify-center">
                        <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
                    </div>
                )}
                {!loading && items.length === 0 && (
                    <p className="p-8 text-center text-zinc-500">No liked videos yet</p>
                )}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {items.map((v) => (
                        <Link
                            key={v.id}
                            href={`/feed?v=${v.id}`}
                            className="aspect-[9/16] bg-zinc-900 rounded-lg overflow-hidden relative group"
                        >
                            {v.thumbnail_url && (
                                <img
                                    src={v.thumbnail_url}
                                    alt={v.title}
                                    className="w-full h-full object-cover"
                                />
                            )}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-90" />
                            <div className="absolute bottom-2 left-2 right-2 text-xs">
                                <div className="font-semibold line-clamp-2">{v.title}</div>
                                <div className="text-white/60 mt-1">
                                    {v.views} views · {v.likes} ♥
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            </div>
        </div>
    );
}
