'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { Heart, MessageCircle, Share2, Flag, Volume2, VolumeX, Pause, Plus, Settings as SettingsIcon, User as UserIcon, DollarSign, Lock, Crown } from 'lucide-react';
import { NotificationBell } from '@/components/notifications/notification-bell';
import { apiClient, getBaseUrl } from '@/lib/api/client';
import { interactionService } from '@/lib/api/interactions';
import { videoService, type CaptionDTO } from '@/lib/api/video';
import type { PaginatedVideoResponse, VideoResponseDTO } from '@/lib/types';
import { useAuthStore } from '@/lib/auth/auth-store';
import { CommentSheet } from './comment-sheet';

type FeedType = 'foryou' | 'following' | 'trending';

interface MobileVideoFeedProps {
    initialFeedType?: FeedType;
}

const PAGE_SIZE = 10;

export function MobileVideoFeed({ initialFeedType = 'foryou' }: MobileVideoFeedProps) {
    const { user } = useAuthStore();
    const [feedType, setFeedType] = useState<FeedType>(initialFeedType);
    const [videos, setVideos] = useState<VideoResponseDTO[]>([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [activeIndex, setActiveIndex] = useState(0);
    const [muted, setMuted] = useState(true);
    const [openComments, setOpenComments] = useState<string | null>(null);

    const containerRef = useRef<HTMLDivElement>(null);
    const itemRefs = useRef<Map<number, HTMLDivElement>>(new Map());
    const videoRefs = useRef<Map<number, HTMLVideoElement>>(new Map());

    const fetchPage = useCallback(
        async (pageNum: number) => {
            setLoading(true);
            try {
                const endpoint = user
                    ? `/feed/?feed_type=${feedType}&page=${pageNum}&page_size=${PAGE_SIZE}`
                    : `/feed/trending?page=${pageNum}&page_size=${PAGE_SIZE}`;
                const data = await apiClient<PaginatedVideoResponse>(endpoint);
                setVideos((prev) =>
                    pageNum === 1 ? data.items : [...prev, ...data.items],
                );
                setHasMore(pageNum < data.total_pages);
                setPage(pageNum);
            } catch (err) {
                console.error('feed fetch failed', err);
            } finally {
                setLoading(false);
            }
        },
        [feedType, user],
    );

    // Pull-to-refresh: track downward drag at top of feed.
    const [pullY, setPullY] = useState(0);
    const [refreshing, setRefreshing] = useState(false);
    const touchStartY = useRef<number | null>(null);

    const onTouchStart = (e: React.TouchEvent) => {
        const el = containerRef.current;
        if (el && el.scrollTop <= 0) {
            touchStartY.current = e.touches[0].clientY;
        }
    };
    const onTouchMove = (e: React.TouchEvent) => {
        if (touchStartY.current === null) return;
        const delta = e.touches[0].clientY - touchStartY.current;
        if (delta > 0) {
            setPullY(Math.min(delta, 120));
        }
    };
    const onTouchEnd = async () => {
        const y = pullY;
        touchStartY.current = null;
        setPullY(0);
        if (y > 70 && !refreshing) {
            setRefreshing(true);
            await fetchPage(1);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        setVideos([]);
        setActiveIndex(0);
        setHasMore(true);
        fetchPage(1);
    }, [fetchPage]);

    // IntersectionObserver: track which video is in view
    useEffect(() => {
        if (!containerRef.current) return;
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((e) => {
                    if (e.intersectionRatio > 0.7) {
                        const idx = Number(e.target.getAttribute('data-idx'));
                        setActiveIndex(idx);
                    }
                });
            },
            { root: containerRef.current, threshold: [0.7] },
        );
        itemRefs.current.forEach((el) => observer.observe(el));
        return () => observer.disconnect();
    }, [videos]);

    // Play active video, pause others
    useEffect(() => {
        videoRefs.current.forEach((vid, idx) => {
            if (idx === activeIndex) {
                vid.muted = muted;
                vid.play().catch(() => {
                    // autoplay blocked; user must tap
                });
            } else {
                vid.pause();
                vid.currentTime = 0;
            }
        });
    }, [activeIndex, videos, muted]);

    // Infinite scroll: load next page when near the bottom
    useEffect(() => {
        if (videos.length === 0) return;
        if (activeIndex >= videos.length - 3 && hasMore && !loading) {
            fetchPage(page + 1);
        }
    }, [activeIndex, videos.length, hasMore, loading, page, fetchPage]);

    return (
        <div className="fixed inset-0 bg-black overflow-hidden text-white">
            {/* Top bar: profile (left) + tab switcher (center) + settings (right) */}
            <div className="absolute top-[max(env(safe-area-inset-top),12px)] left-0 right-0 z-30 flex items-center px-3 pointer-events-none">
                {user ? (
                    <Link
                        href={`/profile?u=${user.username}`}
                        className="pointer-events-auto bg-black/30 backdrop-blur rounded-full p-2"
                        aria-label="My profile"
                    >
                        <UserIcon className="w-5 h-5 text-white" />
                    </Link>
                ) : (
                    <Link
                        href="/login"
                        className="pointer-events-auto bg-white/10 backdrop-blur rounded-full px-3 py-1 text-sm font-semibold"
                    >
                        Log in
                    </Link>
                )}
                <div className="flex-1 flex justify-center gap-6 text-sm font-semibold">
                    {(['following', 'foryou', 'trending'] as FeedType[]).map((t) => (
                        <button
                            key={t}
                            onClick={() => setFeedType(t)}
                            className={`pointer-events-auto px-3 py-1 rounded-full transition ${
                                feedType === t
                                    ? 'text-white drop-shadow-md'
                                    : 'text-white/60'
                            }`}
                        >
                            {t === 'foryou' ? 'For You' : t === 'following' ? 'Following' : 'Trending'}
                        </button>
                    ))}
                </div>
                {user && (
                    <div className="flex items-center gap-2">
                        <NotificationBell />
                        <Link
                            href="/settings"
                            className="pointer-events-auto bg-black/30 backdrop-blur rounded-full p-2"
                            aria-label="Settings"
                        >
                            <SettingsIcon className="w-5 h-5 text-white" />
                        </Link>
                    </div>
                )}
            </div>

            {/* Pull-to-refresh indicator */}
            {(pullY > 0 || refreshing) && (
                <div
                    className="absolute top-0 left-0 right-0 z-40 flex justify-center pointer-events-none"
                    style={{ transform: `translateY(${refreshing ? 60 : pullY}px)` }}
                >
                    <div className="mt-2 bg-black/60 rounded-full px-3 py-1 text-xs">
                        {refreshing ? 'Refreshing…' : pullY > 70 ? 'Release to refresh' : 'Pull to refresh'}
                    </div>
                </div>
            )}

            {/* Feed */}
            <div
                ref={containerRef}
                className="h-full overflow-y-scroll snap-y snap-mandatory scroll-smooth"
                style={{ scrollSnapType: 'y mandatory', WebkitOverflowScrolling: 'touch' }}
                onTouchStart={onTouchStart}
                onTouchMove={onTouchMove}
                onTouchEnd={onTouchEnd}
            >
                {videos.map((video, idx) => (
                    <FeedItem
                        key={video.id}
                        idx={idx}
                        video={video}
                        muted={muted}
                        onToggleMute={() => setMuted((m) => !m)}
                        onOpenComments={() => setOpenComments(video.id)}
                        registerItem={(el) => {
                            if (el) itemRefs.current.set(idx, el);
                            else itemRefs.current.delete(idx);
                        }}
                        registerVideo={(el) => {
                            if (el) videoRefs.current.set(idx, el);
                            else videoRefs.current.delete(idx);
                        }}
                    />
                ))}
                {videos.length === 0 && !loading && (
                    <div className="h-full flex flex-col items-center justify-center gap-3 text-white/60">
                        <span className="text-lg">No videos yet</span>
                        <Link href="/discover" className="underline text-white">
                            Browse discover →
                        </Link>
                    </div>
                )}
                {loading && (
                    <div className="h-screen flex items-center justify-center text-white/60">
                        Loading…
                    </div>
                )}
            </div>

            {/* Floating record button */}
            {user && (
                <Link
                    href="/record"
                    className="absolute right-4 bottom-[max(env(safe-area-inset-bottom),20px)] z-30 w-14 h-14 rounded-full bg-gradient-to-br from-pink-500 via-red-500 to-yellow-400 flex items-center justify-center shadow-2xl"
                    aria-label="New post"
                >
                    <Plus className="w-7 h-7 text-white" />
                </Link>
            )}

            {openComments && (
                <CommentSheet
                    videoId={openComments}
                    onClose={() => setOpenComments(null)}
                />
            )}
        </div>
    );
}

interface FeedItemProps {
    idx: number;
    video: VideoResponseDTO;
    muted: boolean;
    onToggleMute: () => void;
    onOpenComments: () => void;
    registerItem: (el: HTMLDivElement | null) => void;
    registerVideo: (el: HTMLVideoElement | null) => void;
}

function FeedItem({
    idx,
    video,
    muted,
    onToggleMute,
    onOpenComments,
    registerItem,
    registerVideo,
}: FeedItemProps) {
    const [liked, setLiked] = useState(false);
    const [likeCount, setLikeCount] = useState(video.likes);
    const [paused, setPaused] = useState(false);
    const [captions, setCaptions] = useState<CaptionDTO[]>([]);
    const [currentCaption, setCurrentCaption] = useState<string | null>(null);
    const videoRef = useRef<HTMLVideoElement | null>(null);

    useEffect(() => {
        let cancelled = false;
        videoService
            .getCaptions(video.id)
            .then((list) => {
                if (!cancelled) setCaptions(list);
            })
            .catch(() => {});
        return () => {
            cancelled = true;
        };
    }, [video.id]);

    useEffect(() => {
        const vid = videoRef.current;
        if (!vid || captions.length === 0) return;
        const onTime = () => {
            const t = vid.currentTime;
            const active = captions.find((c) => t >= c.start_time && t <= c.end_time);
            setCurrentCaption(active?.text ?? null);
        };
        vid.addEventListener('timeupdate', onTime);
        return () => vid.removeEventListener('timeupdate', onTime);
    }, [captions]);

    const togglePlay = () => {
        const vid = videoRef.current;
        if (!vid) return;
        if (vid.paused) {
            vid.play();
            setPaused(false);
        } else {
            vid.pause();
            setPaused(true);
        }
    };

    const onLike = async () => {
        // Optimistic
        setLiked((l) => !l);
        setLikeCount((c) => (liked ? c - 1 : c + 1));
        try {
            await interactionService.toggleLike(video.id);
        } catch {
            // revert
            setLiked((l) => !l);
            setLikeCount((c) => (liked ? c + 1 : c - 1));
        }
    };

    const onShare = async () => {
        const url = `${window.location.origin}/profile?u=${video.creator_id}`;
        if (navigator.share) {
            try {
                await navigator.share({ title: video.title, url });
            } catch {}
        } else {
            await navigator.clipboard.writeText(url);
        }
    };

    const onReport = async () => {
        const choice = window.prompt(
            'Pick an action:\n  r = report this video\n  b = block @' + video.creator_id,
        );
        if (!choice) return;
        if (choice.toLowerCase().startsWith('b')) {
            if (!window.confirm(`Block @${video.creator_id}? You'll no longer see their content.`)) return;
            try {
                await apiClient(`/users/${video.creator_id}/block`, { method: 'POST' });
                alert('User blocked.');
            } catch {
                alert('Could not block. Try again.');
            }
            return;
        }
        const reason = window.prompt(
            'Why are you reporting this video?\n(spam, harmful, harassment, copyright, other)',
        );
        if (!reason) return;
        try {
            await apiClient(`/videos/${video.id}/report`, {
                method: 'POST',
                body: JSON.stringify({ reason }),
            });
            alert('Thanks. Our team will review.');
        } catch {
            alert('Could not submit report. Try again.');
        }
    };

    return (
        <div
            ref={registerItem}
            data-idx={idx}
            className="relative h-screen w-full snap-start snap-always"
            style={{ scrollSnapAlign: 'start' }}
        >
            {/* Video (or premium-locked overlay) */}
            {video.is_locked ? (
                <div className="absolute inset-0 bg-zinc-900">
                    {video.thumbnail_url && (
                        <img
                            src={video.thumbnail_url}
                            alt=""
                            className="absolute inset-0 w-full h-full object-cover blur-2xl scale-110 opacity-40"
                        />
                    )}
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center text-white p-6 z-10">
                        <Crown className="w-14 h-14 text-amber-400 mb-3" />
                        <div className="text-xl font-bold mb-1">Premium content</div>
                        <p className="text-sm text-white/70 mb-4 max-w-xs">
                            Subscribe to @{video.creator_username ?? video.creator_id} to unlock
                        </p>
                        <button
                            onClick={async (e) => {
                                e.stopPropagation();
                                const raw = window.prompt('Monthly amount in USD?', '4.99');
                                if (!raw) return;
                                const amount = parseFloat(raw);
                                if (!Number.isFinite(amount) || amount <= 0) return;
                                try {
                                    const fd = new FormData();
                                    fd.append('creator_id', video.creator_id);
                                    fd.append('amount', String(amount));
                                    fd.append('interval', 'month');
                                    const res = await fetch(`${getBaseUrl()}/api/payments/subscriptions`, {
                                        method: 'POST',
                                        credentials: 'include',
                                        body: fd,
                                    });
                                    if (!res.ok) throw new Error(await res.text());
                                    alert('Subscription started. Refresh in a moment.');
                                } catch (e) {
                                    alert(e instanceof Error ? e.message : 'Subscribe failed');
                                }
                            }}
                            className="px-6 py-3 rounded-full bg-amber-500 text-white font-semibold flex items-center gap-2"
                        >
                            <Lock className="w-4 h-4" />
                            Subscribe
                        </button>
                    </div>
                </div>
            ) : (
                <video
                    ref={(el) => {
                        videoRef.current = el;
                        registerVideo(el);
                    }}
                    src={video.url ?? undefined}
                    poster={video.thumbnail_url ?? undefined}
                    className="absolute inset-0 w-full h-full object-cover"
                    playsInline
                    loop
                    muted={muted}
                    preload="metadata"
                    onClick={togglePlay}
                />
            )}

            {/* Pause indicator */}
            {paused && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="bg-black/40 rounded-full p-6">
                        <Pause className="w-12 h-12 text-white" />
                    </div>
                </div>
            )}

            {/* Caption overlay */}
            {currentCaption && (
                <div className="absolute bottom-[max(env(safe-area-inset-bottom),120px)] left-0 right-0 flex justify-center pointer-events-none px-6 z-10">
                    <div className="bg-black/70 backdrop-blur text-white px-3 py-2 rounded-md text-sm font-medium max-w-md text-center">
                        {currentCaption}
                    </div>
                </div>
            )}

            {/* Mute toggle */}
            <button
                onClick={onToggleMute}
                className="absolute top-[max(env(safe-area-inset-top),12px)] right-3 z-20 bg-black/40 backdrop-blur rounded-full p-2"
                aria-label={muted ? 'Unmute' : 'Mute'}
            >
                {muted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
            </button>

            {/* Right-side actions */}
            <div className="absolute right-3 bottom-32 z-20 flex flex-col items-center gap-5">
                <ActionButton
                    icon={<Heart className={`w-7 h-7 ${liked ? 'fill-red-500 text-red-500' : ''}`} />}
                    label={formatCount(likeCount)}
                    onClick={onLike}
                />
                <ActionButton
                    icon={<MessageCircle className="w-7 h-7" />}
                    label={formatCount(video.comments ?? 0)}
                    onClick={onOpenComments}
                />
                <ActionButton
                    icon={<Share2 className="w-7 h-7" />}
                    label="Share"
                    onClick={onShare}
                />
                <ActionButton
                    icon={<DollarSign className="w-6 h-6" />}
                    label="Tip"
                    onClick={async () => {
                        const raw = window.prompt('Tip amount in USD?', '1.00');
                        if (!raw) return;
                        const amount = parseFloat(raw);
                        if (!Number.isFinite(amount) || amount <= 0) {
                            alert('Invalid amount');
                            return;
                        }
                        try {
                            const fd = new FormData();
                            fd.append('creator_id', video.creator_id);
                            fd.append('amount', String(amount));
                            fd.append('video_id', video.id);
                            const res = await fetch(`${getBaseUrl()}/api/payments/tip`, {
                                method: 'POST',
                                credentials: 'include',
                                body: fd,
                            });
                            if (!res.ok) throw new Error(await res.text());
                            alert('Thanks for the tip!');
                        } catch (e) {
                            alert(e instanceof Error ? e.message : 'Tip failed');
                        }
                    }}
                />
                <ActionButton
                    icon={<Flag className="w-6 h-6" />}
                    label="Report"
                    onClick={onReport}
                />
            </div>

            {/* Bottom info */}
            <div className="absolute left-3 right-20 bottom-[max(env(safe-area-inset-bottom),16px)] z-20 space-y-2">
                <Link
                    href={`/profile?u=${video.creator_username ?? video.creator_id}`}
                    className="font-bold text-base inline-block"
                >
                    @{video.creator_username ?? video.creator_id}
                </Link>
                <div className="text-xs text-white/60">
                    {formatCount(video.views)} views
                </div>
                <p className="text-sm leading-snug line-clamp-2">
                    <RichText text={video.title} />
                </p>
                {video.description && (
                    <p className="text-xs text-white/80 line-clamp-2">
                        <RichText text={video.description} />
                    </p>
                )}
            </div>
        </div>
    );
}

/** Render text with #hashtags and @mentions as inline links. */
function RichText({ text }: { text: string }) {
    if (!text) return null;
    const parts = text.split(/(#[\w]+|@[\w-]+)/g);
    return (
        <>
            {parts.map((p, i) => {
                if (p.startsWith('#')) {
                    return (
                        <Link
                            key={i}
                            href={`/search?q=${encodeURIComponent(p)}`}
                            className="text-blue-300 hover:text-blue-200"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {p}
                        </Link>
                    );
                }
                if (p.startsWith('@')) {
                    return (
                        <Link
                            key={i}
                            href={`/profile?u=${p.slice(1)}`}
                            className="text-blue-300 hover:text-blue-200"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {p}
                        </Link>
                    );
                }
                return <span key={i}>{p}</span>;
            })}
        </>
    );
}

function ActionButton({
    icon,
    label,
    onClick,
}: {
    icon: React.ReactNode;
    label: string;
    onClick: () => void;
}) {
    return (
        <button
            onClick={onClick}
            className="flex flex-col items-center gap-1 active:scale-90 transition"
        >
            <div className="bg-black/30 backdrop-blur rounded-full p-2">{icon}</div>
            <span className="text-xs">{label}</span>
        </button>
    );
}

function formatCount(n: number): string {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return String(n);
}
