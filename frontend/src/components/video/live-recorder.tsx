'use client';

import { useEffect, useRef, useState } from 'react';
import { Camera, Square, RotateCcw, CheckCircle2 } from 'lucide-react';
import { BgRemover } from './bg-remover';

type BgMode = 'off' | 'blur' | 'green';

interface LiveRecorderProps {
    onComplete: (file: File, durationSeconds: number) => void;
    maxSeconds?: number;
    width?: number;
    height?: number;
}

export function LiveRecorder({
    onComplete,
    maxSeconds = 60,
    width = 720,
    height = 1280,
}: LiveRecorderProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const recorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);
    const startTimeRef = useRef<number>(0);
    const tickerRef = useRef<number | null>(null);
    const camStreamRef = useRef<MediaStream | null>(null);

    const [streamReady, setStreamReady] = useState(false);
    const [recording, setRecording] = useState(false);
    const [elapsed, setElapsed] = useState(0);
    const [bgMode, setBgMode] = useState<BgMode>('off');
    const [error, setError] = useState<string | null>(null);

    // Acquire camera + mic
    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'user', width, height },
                    audio: true,
                });
                if (cancelled) {
                    stream.getTracks().forEach((t) => t.stop());
                    return;
                }
                camStreamRef.current = stream;
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    await videoRef.current.play().catch(() => {});
                }
                setStreamReady(true);
            } catch (e) {
                setError(
                    e instanceof Error ? e.message : 'Could not access camera',
                );
            }
        })();
        return () => {
            cancelled = true;
            camStreamRef.current?.getTracks().forEach((t) => t.stop());
            if (tickerRef.current) window.clearInterval(tickerRef.current);
        };
    }, [width, height]);

    const start = () => {
        if (!camStreamRef.current) return;
        chunksRef.current = [];

        // If BG removal is on, capture the canvas (which has the masked
        // composition) + audio from the original mic. Otherwise capture
        // the camera stream directly.
        let recordStream: MediaStream;
        if (bgMode !== 'off' && canvasRef.current) {
            const canvasStream = canvasRef.current.captureStream(30);
            const audioTrack = camStreamRef.current.getAudioTracks()[0];
            if (audioTrack) canvasStream.addTrack(audioTrack);
            recordStream = canvasStream;
        } else {
            recordStream = camStreamRef.current;
        }

        const mime = MediaRecorder.isTypeSupported('video/mp4')
            ? 'video/mp4'
            : MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus')
              ? 'video/webm;codecs=vp9,opus'
              : 'video/webm';
        const recorder = new MediaRecorder(recordStream, { mimeType: mime });
        recorder.ondataavailable = (e) => {
            if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
        };
        recorder.onstop = () => {
            const blob = new Blob(chunksRef.current, { type: mime });
            const ext = mime.includes('mp4') ? 'mp4' : 'webm';
            const file = new File([blob], `clip-${Date.now()}.${ext}`, { type: mime });
            const dur = (Date.now() - startTimeRef.current) / 1000;
            onComplete(file, dur);
        };

        startTimeRef.current = Date.now();
        recorder.start(250);
        recorderRef.current = recorder;
        setRecording(true);
        setElapsed(0);

        tickerRef.current = window.setInterval(() => {
            const e = (Date.now() - startTimeRef.current) / 1000;
            setElapsed(e);
            if (e >= maxSeconds) stop();
        }, 100);
    };

    const stop = () => {
        if (tickerRef.current) window.clearInterval(tickerRef.current);
        recorderRef.current?.stop();
        setRecording(false);
    };

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center gap-3 p-8 text-white">
                <p className="text-red-400">{error}</p>
                <p className="text-xs text-zinc-500">
                    Allow camera + microphone access in your browser/iOS Settings
                    and try again.
                </p>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-3">
            {/* Preview surface */}
            <div className="relative rounded-xl overflow-hidden bg-zinc-900 aspect-[9/16]">
                {/* Hidden source video for the segmenter */}
                <video
                    ref={videoRef}
                    playsInline
                    muted
                    className={bgMode === 'off' ? 'absolute inset-0 w-full h-full object-cover' : 'hidden'}
                />
                {/* Composited output canvas (visible when BG removal is on) */}
                <canvas
                    ref={canvasRef}
                    width={width}
                    height={height}
                    className={bgMode === 'off' ? 'hidden' : 'absolute inset-0 w-full h-full object-cover'}
                />
                <BgRemover
                    videoRef={videoRef}
                    outputRef={canvasRef}
                    mode={bgMode}
                    width={width}
                    height={height}
                />

                {/* HUD: timer / record dot */}
                {recording && (
                    <div className="absolute top-3 left-3 flex items-center gap-2 bg-black/60 px-2 py-1 rounded-full text-white text-xs">
                        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                        {elapsed.toFixed(1)}s
                    </div>
                )}
                {!streamReady && (
                    <div className="absolute inset-0 flex items-center justify-center text-white/60">
                        Loading camera…
                    </div>
                )}
            </div>

            {/* BG mode picker */}
            <div className="flex items-center justify-center gap-2 text-xs">
                {(['off', 'blur', 'green'] as BgMode[]).map((m) => (
                    <button
                        key={m}
                        onClick={() => setBgMode(m)}
                        className={`px-3 py-1.5 rounded-full ${
                            bgMode === m
                                ? 'bg-white text-black font-semibold'
                                : 'bg-zinc-800 text-zinc-300'
                        }`}
                    >
                        BG: {m === 'off' ? 'on' : m}
                    </button>
                ))}
            </div>

            {/* Record / stop */}
            <div className="flex justify-center">
                {!recording ? (
                    <button
                        onClick={start}
                        disabled={!streamReady}
                        className="w-20 h-20 rounded-full bg-red-500 hover:bg-red-600 disabled:opacity-40 flex items-center justify-center"
                        aria-label="Start recording"
                    >
                        <Camera className="w-9 h-9 text-white" />
                    </button>
                ) : (
                    <button
                        onClick={stop}
                        className="w-20 h-20 rounded-full bg-zinc-200 hover:bg-zinc-300 flex items-center justify-center"
                        aria-label="Stop recording"
                    >
                        <Square className="w-9 h-9 text-red-500 fill-red-500" />
                    </button>
                )}
            </div>

            <div className="text-center text-xs text-zinc-500">
                {recording
                    ? `Recording — auto-stop at ${maxSeconds}s`
                    : `Up to ${maxSeconds}s`}
            </div>
        </div>
    );
}
