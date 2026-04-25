'use client';

import { usePathname } from 'next/navigation';
import { Navbar } from './navbar';

// Routes that should render full-bleed (no top navbar, no padding).
// These are mobile-first immersive experiences.
const FULL_SCREEN_PATTERNS: RegExp[] = [
    /^\/feed(?:\/|$)/,
    /^\/record(?:\/|$)/,
    /^\/settings(?:\/|$)/,
    /^\/legal(?:\/|$)/,
    /^\/profile(?:\/|$)/,
];

export function ChromeShell({ children }: { children: React.ReactNode }) {
    const pathname = usePathname() ?? '/';
    const fullScreen = FULL_SCREEN_PATTERNS.some((re) => re.test(pathname));

    if (fullScreen) {
        return <main className="min-h-screen">{children}</main>;
    }

    return (
        <>
            <Navbar />
            <main className="pt-24 min-h-screen">{children}</main>
        </>
    );
}
