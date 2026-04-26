'use client';

import { useEffect, useRef, useState } from 'react';

/**
 * Live background removal using MediaPipe Selfie Segmentation. Runs in the
 * browser — no server compute. Mode: 'remove' draws solid background, 'blur'
 * applies a Gaussian blur to the original frame.
 *
 * The component owns its own canvas. Parent passes the source <video> element
 * via the `videoRef` prop. The composed result is written to `outputRef.current`
 * which the parent can use for preview or capture.
 */

type Mode = 'off' | 'blur' | 'green';

interface BgRemoverProps {
    videoRef: React.RefObject<HTMLVideoElement | null>;
    outputRef: React.RefObject<HTMLCanvasElement | null>;
    mode: Mode;
    width?: number;
    height?: number;
}

export function BgRemover({ videoRef, outputRef, mode, width = 720, height = 1280 }: BgRemoverProps) {
    const segmenterRef = useRef<unknown>(null);
    const rafRef = useRef<number | null>(null);
    const [ready, setReady] = useState(false);

    useEffect(() => {
        if (mode === 'off') {
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
            return;
        }
        let cancelled = false;

        (async () => {
            // Dynamic import — keeps MediaPipe out of the main bundle when not needed.
            const mp = await import('@mediapipe/selfie_segmentation');
            const Segmenter = mp.SelfieSegmentation as unknown as new (cfg: {
                locateFile: (f: string) => string;
            }) => {
                setOptions: (o: { modelSelection: number }) => void;
                onResults: (cb: (r: { image: HTMLCanvasElement | HTMLVideoElement; segmentationMask: HTMLCanvasElement }) => void) => void;
                send: (i: { image: HTMLCanvasElement | HTMLVideoElement }) => Promise<void>;
                close: () => void;
            };

            const seg = new Segmenter({
                locateFile: (file: string) =>
                    `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${file}`,
            });
            seg.setOptions({ modelSelection: 1 });

            seg.onResults((results) => {
                const out = outputRef.current;
                const vid = videoRef.current;
                if (!out || !vid || cancelled) return;
                const ctx = out.getContext('2d');
                if (!ctx) return;

                ctx.save();
                ctx.clearRect(0, 0, out.width, out.height);

                if (mode === 'green') {
                    // Solid green background, person on top
                    ctx.fillStyle = '#00ff00';
                    ctx.fillRect(0, 0, out.width, out.height);
                } else if (mode === 'blur') {
                    // Blurred original frame as background
                    ctx.filter = 'blur(20px)';
                    ctx.drawImage(vid, 0, 0, out.width, out.height);
                    ctx.filter = 'none';
                }

                // Composite the person on top using the segmentation mask
                ctx.globalCompositeOperation = 'destination-out';
                ctx.drawImage(results.segmentationMask, 0, 0, out.width, out.height);
                ctx.globalCompositeOperation = 'destination-over';
                ctx.drawImage(vid, 0, 0, out.width, out.height);
                ctx.restore();
            });

            segmenterRef.current = seg;
            setReady(true);

            const tick = async () => {
                if (cancelled) return;
                const vid = videoRef.current;
                if (vid && !vid.paused && vid.readyState >= 2) {
                    try {
                        await seg.send({ image: vid });
                    } catch {
                        /* ignore frame errors */
                    }
                }
                rafRef.current = requestAnimationFrame(tick);
            };
            rafRef.current = requestAnimationFrame(tick);
        })().catch((e) => console.warn('[bg-remover] init failed', e));

        return () => {
            cancelled = true;
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
            const seg = segmenterRef.current as { close?: () => void } | null;
            try {
                seg?.close?.();
            } catch {}
        };
    }, [mode, videoRef, outputRef]);

    return (
        <div className="absolute top-2 left-2 z-30 text-[10px] text-white/70 pointer-events-none">
            {mode !== 'off' && !ready && 'Loading bg removal…'}
        </div>
    );
}
