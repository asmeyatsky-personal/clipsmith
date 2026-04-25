import type { NextConfig } from "next";

// Capacitor requires a static SPA. `output: "export"` produces `out/`
// which Capacitor copies into the iOS bundle.
//
// Headers() and image optimization are incompatible with static export —
// security headers are enforced by the FastAPI backend and (when served
// via web) the CDN. The Capacitor binary doesn't pass through Next's
// middleware anyway.
const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: {
    unoptimized: true,
    remotePatterns: [
      { protocol: "http", hostname: "localhost" },
      { protocol: "https", hostname: "**.clipsmith.com" },
      { protocol: "https", hostname: "**.clipsmith.app" },
      { protocol: "https", hostname: "**.r2.cloudflarestorage.com" },
      { protocol: "https", hostname: "**.amazonaws.com" },
      { protocol: "https", hostname: "**.cloudfront.net" },
    ],
  },
};

export default nextConfig;
