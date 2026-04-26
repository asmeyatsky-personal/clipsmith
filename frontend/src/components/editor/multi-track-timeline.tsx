'use client';

import { useEffect, useRef, useState } from 'react';

/**
 * Phase 2.6 — Multi-track timeline v1.
 *
 * Three tracks (video / text / music). Each track has draggable clips.
 * Pure HTML/CSS — no Konva dependency to keep the bundle small. We can
 * upgrade to Konva when keyframes / non-linear scrubbing become real
 * requirements.
 */

export type TrackType = 'video' | 'text' | 'music';

export interface TimelineClip {
    id: string;
    start: number; // seconds
    end: number; // seconds
    label: string;
    color?: string;
}

export interface TimelineTrack {
    id: string;
    type: TrackType;
    clips: TimelineClip[];
}

interface MultiTrackTimelineProps {
    tracks: TimelineTrack[];
    duration: number;
    playhead: number;
    onPlayheadChange?: (t: number) => void;
    onClipChange?: (trackId: string, clip: TimelineClip) => void;
    pxPerSecond?: number;
}

const TRACK_HEIGHT = 56;
const TRACK_GAP = 8;
const TRACK_LABEL_WIDTH = 64;

const TRACK_BG: Record<TrackType, string> = {
    video: 'bg-blue-500/30',
    text: 'bg-amber-500/30',
    music: 'bg-purple-500/30',
};
const CLIP_BG: Record<TrackType, string> = {
    video: 'bg-blue-500',
    text: 'bg-amber-500',
    music: 'bg-purple-500',
};

export function MultiTrackTimeline({
    tracks,
    duration,
    playhead,
    onPlayheadChange,
    onClipChange,
    pxPerSecond = 60,
}: MultiTrackTimelineProps) {
    const trackAreaRef = useRef<HTMLDivElement>(null);
    const [width, setWidth] = useState(0);

    useEffect(() => {
        if (!trackAreaRef.current) return;
        const ro = new ResizeObserver((entries) => {
            setWidth(entries[0].contentRect.width);
        });
        ro.observe(trackAreaRef.current);
        return () => ro.disconnect();
    }, []);

    const totalWidth = Math.max(width, duration * pxPerSecond);

    const handleScrub = (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const t = (x / pxPerSecond);
        onPlayheadChange?.(Math.max(0, Math.min(duration, t)));
    };

    return (
        <div className="bg-zinc-950 text-white rounded-lg p-3">
            <div className="flex items-center gap-2 text-xs text-zinc-400 mb-2">
                <span>Tracks</span>
                <div className="flex-1 text-right">
                    {playhead.toFixed(2)}s / {duration.toFixed(2)}s
                </div>
            </div>

            <div className="flex gap-2">
                {/* Track labels */}
                <div className="flex flex-col gap-2" style={{ width: TRACK_LABEL_WIDTH }}>
                    {tracks.map((t) => (
                        <div
                            key={t.id}
                            style={{ height: TRACK_HEIGHT }}
                            className="flex items-center text-xs uppercase font-semibold text-zinc-500"
                        >
                            {t.type}
                        </div>
                    ))}
                </div>

                {/* Track area */}
                <div className="flex-1 overflow-x-auto" ref={trackAreaRef}>
                    <div
                        className="relative"
                        style={{ width: totalWidth, minWidth: '100%' }}
                    >
                        {/* Time ruler */}
                        <div
                            className="relative h-5 mb-1 cursor-pointer select-none"
                            onClick={handleScrub}
                        >
                            {Array.from({ length: Math.ceil(duration) + 1 }).map((_, s) => (
                                <div
                                    key={s}
                                    className="absolute top-0 h-full text-[10px] text-zinc-500 border-l border-zinc-800"
                                    style={{ left: s * pxPerSecond, paddingLeft: 2 }}
                                >
                                    {s}s
                                </div>
                            ))}
                        </div>

                        {/* Tracks */}
                        <div className="flex flex-col gap-2">
                            {tracks.map((track) => (
                                <div
                                    key={track.id}
                                    className={`relative rounded ${TRACK_BG[track.type]}`}
                                    style={{ height: TRACK_HEIGHT }}
                                >
                                    {track.clips.map((clip) => (
                                        <Clip
                                            key={clip.id}
                                            track={track}
                                            clip={clip}
                                            pxPerSecond={pxPerSecond}
                                            duration={duration}
                                            onChange={(updated) =>
                                                onClipChange?.(track.id, updated)
                                            }
                                        />
                                    ))}
                                </div>
                            ))}
                        </div>

                        {/* Playhead */}
                        <div
                            className="absolute top-0 bottom-0 w-px bg-red-500 pointer-events-none"
                            style={{ left: playhead * pxPerSecond, top: 0 }}
                        >
                            <div className="absolute -top-1 -left-1 w-3 h-3 rounded-full bg-red-500" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

interface ClipProps {
    track: TimelineTrack;
    clip: TimelineClip;
    duration: number;
    pxPerSecond: number;
    onChange: (clip: TimelineClip) => void;
}

function Clip({ track, clip, pxPerSecond, duration, onChange }: ClipProps) {
    const startPx = clip.start * pxPerSecond;
    const widthPx = (clip.end - clip.start) * pxPerSecond;

    const onMouseDown = (e: React.MouseEvent, mode: 'move' | 'left' | 'right') => {
        e.stopPropagation();
        const startX = e.clientX;
        const origStart = clip.start;
        const origEnd = clip.end;

        const move = (ev: MouseEvent) => {
            const dx = (ev.clientX - startX) / pxPerSecond;
            let next = clip;
            if (mode === 'move') {
                const length = origEnd - origStart;
                const newStart = Math.max(0, Math.min(duration - length, origStart + dx));
                next = { ...clip, start: newStart, end: newStart + length };
            } else if (mode === 'left') {
                const newStart = Math.max(0, Math.min(origEnd - 0.2, origStart + dx));
                next = { ...clip, start: newStart };
            } else {
                const newEnd = Math.min(duration, Math.max(origStart + 0.2, origEnd + dx));
                next = { ...clip, end: newEnd };
            }
            onChange(next);
        };
        const up = () => {
            window.removeEventListener('mousemove', move);
            window.removeEventListener('mouseup', up);
        };
        window.addEventListener('mousemove', move);
        window.addEventListener('mouseup', up);
    };

    return (
        <div
            className={`absolute top-1 bottom-1 rounded ${CLIP_BG[track.type]} text-white text-xs px-2 flex items-center cursor-grab active:cursor-grabbing select-none shadow-lg`}
            style={{ left: startPx, width: widthPx }}
            onMouseDown={(e) => onMouseDown(e, 'move')}
        >
            <div
                onMouseDown={(e) => onMouseDown(e, 'left')}
                className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize bg-white/30 rounded-l"
            />
            <span className="truncate">{clip.label}</span>
            <div
                onMouseDown={(e) => onMouseDown(e, 'right')}
                className="absolute right-0 top-0 bottom-0 w-1 cursor-ew-resize bg-white/30 rounded-r"
            />
        </div>
    );
}
