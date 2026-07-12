/**
 * Build-time feature flags. These mirror the backend gates
 * (AI_GENERATION_ENABLED / LIVE_STREAMING_ENABLED). Both default OFF because no
 * provider/worker/SFU processes these flows yet — surfacing them would let a
 * user kick off work that never completes. Set the corresponding
 * NEXT_PUBLIC_* env var to "true" at build time to re-enable once the backend
 * is wired.
 *
 * NEXT_PUBLIC_* values are inlined at build time (static export), so flipping a
 * flag requires a rebuild.
 */
export const FEATURES = {
  aiGeneration: process.env.NEXT_PUBLIC_AI_GENERATION === 'true',
  liveStreaming: process.env.NEXT_PUBLIC_LIVE_STREAMING === 'true',
} as const;
