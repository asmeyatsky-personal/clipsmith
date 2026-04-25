'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, RotateCcw, Upload, Camera, Loader2, Scissors } from 'lucide-react';
import { Haptics, ImpactStyle } from '@capacitor/haptics';
import { Capacitor } from '@capacitor/core';
import { useAuthStore } from '@/lib/auth/auth-store';
import { getBaseUrl } from '@/lib/api/client';

const MAX_DURATION_SECONDS = 60;
const MAX_FILE_BYTES = 500 * 1024 * 1024;

export default function RecordPage() {
    const router = useRouter();
    const { user } = useAuthStore();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const previewRef = useRef<HTMLVideoElement>(null);

    const [file, setFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [duration, setDuration] = useState(0);
    const [trimStart, setTrimStart] = useState(0);
    const [trimEnd, setTrimEnd] = useState(0);
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        return () => {
            if (previewUrl) URL.revokeObjectURL(previewUrl);
        };
    }, [previewUrl]);

    const onPickFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const f = e.target.files?.[0];
        if (!f) return;
        if (f.size > MAX_FILE_BYTES) {
            setError(`File too large (max ${MAX_FILE_BYTES / 1024 / 1024} MB)`);
            return;
        }
        setError(null);
        if (Capacitor.isNativePlatform()) {
            try {
                await Haptics.impact({ style: ImpactStyle.Light });
            } catch {}
        }
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        const url = URL.createObjectURL(f);
        setFile(f);
        setPreviewUrl(url);
        setTrimStart(0);
        setTrimEnd(0);
    };

    const onLoadedMetadata = () => {
        const vid = previewRef.current;
        if (!vid) return;
        const d = Math.min(vid.duration, MAX_DURATION_SECONDS);
        setDuration(d);
        setTrimEnd(d);
    };

    const reset = () => {
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        setFile(null);
        setPreviewUrl(null);
        setTitle('');
        setDescription('');
        setProgress(0);
        setError(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const upload = async () => {
        if (!file) return;
        if (!title.trim()) {
            setError('Title required');
            return;
        }
        if (duration > MAX_DURATION_SECONDS) {
            setError(`Video must be ≤ ${MAX_DURATION_SECONDS}s`);
            return;
        }

        setUploading(true);
        setError(null);
        setProgress(0);

        const fd = new FormData();
        fd.append('title', title.trim());
        fd.append('description', description.trim());
        fd.append('file', file, file.name);
        // Trim metadata is informational for the server-side worker; if the
        // start/end aren't full-clip, the server may re-cut server-side.
        if (trimStart > 0 || trimEnd < duration) {
            fd.append('trim_start', String(trimStart));
            fd.append('trim_end', String(trimEnd));
        }

        const xhr = new XMLHttpRequest();
        xhr.upload.addEventListener('progress', (evt) => {
            if (evt.lengthComputable) {
                setProgress(Math.round((evt.loaded / evt.total) * 100));
            }
        });
        xhr.addEventListener('load', async () => {
            setUploading(false);
            if (xhr.status >= 200 && xhr.status < 300) {
                if (Capacitor.isNativePlatform()) {
                    try {
                        await Haptics.impact({ style: ImpactStyle.Medium });
                    } catch {}
                }
                router.push('/feed');
            } else {
                let msg = 'Upload failed';
                try {
                    const data = JSON.parse(xhr.responseText);
                    msg = data.detail ?? msg;
                } catch {}
                setError(msg);
            }
        });
        xhr.addEventListener('error', () => {
            setUploading(false);
            setError('Network error');
        });
        xhr.open('POST', `${getBaseUrl()}/videos/`);
        xhr.withCredentials = true;
        xhr.send(fd);
    };

    if (!user) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center gap-3 bg-black text-white p-6">
                <Camera className="w-12 h-12" />
                <p>You must log in to upload</p>
                <button
                    onClick={() => router.push('/login')}
                    className="px-6 py-2 bg-white text-black rounded-full font-semibold"
                >
                    Log in
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white flex flex-col">
            {/* Top bar */}
            <div className="flex items-center justify-between px-4 pt-[max(env(safe-area-inset-top),12px)] pb-3">
                <button onClick={() => router.back()} aria-label="Back">
                    <ArrowLeft className="w-6 h-6" />
                </button>
                <h1 className="font-semibold">New post</h1>
                {file ? (
                    <button onClick={reset} aria-label="Reset">
                        <RotateCcw className="w-5 h-5" />
                    </button>
                ) : (
                    <span className="w-5" />
                )}
            </div>

            {/* Body */}
            <div className="flex-1 flex flex-col px-4 py-3 gap-4 pb-[max(env(safe-area-inset-bottom),16px)]">
                {!file ? (
                    <div className="flex-1 flex flex-col items-center justify-center gap-6">
                        <Camera className="w-20 h-20 text-white/40" />
                        <p className="text-white/70 text-center max-w-xs">
                            Record a clip up to {MAX_DURATION_SECONDS}s, or pick one from your library.
                        </p>
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="px-8 py-3 bg-white text-black rounded-full font-semibold flex items-center gap-2"
                        >
                            <Camera className="w-5 h-5" />
                            Record / pick video
                        </button>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="video/*"
                            capture="user"
                            className="hidden"
                            onChange={onPickFile}
                        />
                        {error && <p className="text-red-400 text-sm">{error}</p>}
                    </div>
                ) : (
                    <>
                        <div className="rounded-xl overflow-hidden bg-zinc-900 aspect-[9/16] relative">
                            {previewUrl && (
                                <video
                                    ref={previewRef}
                                    src={previewUrl}
                                    controls
                                    onLoadedMetadata={onLoadedMetadata}
                                    className="w-full h-full object-cover"
                                />
                            )}
                        </div>

                        {duration > 0 && (
                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-sm text-white/80">
                                    <Scissors className="w-4 h-4" />
                                    Trim ({trimStart.toFixed(1)}s — {trimEnd.toFixed(1)}s)
                                </div>
                                <input
                                    type="range"
                                    min={0}
                                    max={duration}
                                    step={0.1}
                                    value={trimStart}
                                    onChange={(e) => setTrimStart(Math.min(parseFloat(e.target.value), trimEnd - 0.5))}
                                    className="w-full"
                                />
                                <input
                                    type="range"
                                    min={0}
                                    max={duration}
                                    step={0.1}
                                    value={trimEnd}
                                    onChange={(e) => setTrimEnd(Math.max(parseFloat(e.target.value), trimStart + 0.5))}
                                    className="w-full"
                                />
                            </div>
                        )}

                        <input
                            type="text"
                            placeholder="Title (required)"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            maxLength={100}
                            className="w-full px-4 py-3 rounded-lg bg-zinc-900 border border-zinc-800 text-white"
                        />
                        <textarea
                            placeholder="Description (optional, supports #hashtags)"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            maxLength={1000}
                            rows={3}
                            className="w-full px-4 py-3 rounded-lg bg-zinc-900 border border-zinc-800 text-white resize-none"
                        />

                        {error && <p className="text-red-400 text-sm">{error}</p>}

                        {uploading && (
                            <div className="space-y-2">
                                <div className="flex justify-between text-xs text-white/60">
                                    <span>Uploading…</span>
                                    <span>{progress}%</span>
                                </div>
                                <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
                                    <div
                                        className="h-full bg-blue-500 transition-all"
                                        style={{ width: `${progress}%` }}
                                    />
                                </div>
                            </div>
                        )}

                        <button
                            onClick={upload}
                            disabled={uploading || !title.trim()}
                            className="mt-auto w-full px-6 py-4 bg-blue-500 disabled:bg-blue-500/40 text-white rounded-full font-semibold flex items-center justify-center gap-2"
                        >
                            {uploading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Upload className="w-5 h-5" />
                            )}
                            {uploading ? 'Uploading' : 'Post'}
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}
