'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function PrivacyPolicyPage() {
    const router = useRouter();
    return (
        <div className="min-h-screen bg-zinc-950 text-white">
            <div className="flex items-center gap-3 px-4 pt-[max(env(safe-area-inset-top),12px)] pb-3 border-b border-zinc-800">
                <button onClick={() => router.back()} aria-label="Back">
                    <ArrowLeft className="w-6 h-6" />
                </button>
                <h1 className="font-semibold">Privacy Policy</h1>
            </div>

            <article className="max-w-2xl mx-auto p-6 prose prose-invert prose-sm">
                <p className="text-xs text-zinc-500">Last updated: 2026-04-25</p>
                <h2>What we collect</h2>
                <ul>
                    <li>
                        <strong>Account data</strong>: username, email, hashed password.
                    </li>
                    <li>
                        <strong>Content</strong>: videos, captions, comments, likes, follows
                        you create.
                    </li>
                    <li>
                        <strong>Device data</strong>: IP address, OS / browser, app version,
                        push notification tokens.
                    </li>
                    <li>
                        <strong>Usage data</strong>: which videos you watch, for how long,
                        and which you interact with — used to rank your feed.
                    </li>
                </ul>

                <h2>How we use it</h2>
                <ul>
                    <li>Authenticate you and prevent abuse.</li>
                    <li>Show you a personalized feed.</li>
                    <li>Send transactional and (with consent) marketing emails / push.</li>
                    <li>Detect prohibited content via automated and human moderation.</li>
                </ul>

                <h2>Sharing</h2>
                <p>
                    We share data only with sub-processors strictly required to operate
                    the service: cloud infrastructure (Neon, Cloudflare), payments
                    (Stripe), error monitoring (Sentry), and email (SMTP provider). We
                    never sell personal data.
                </p>

                <h2>Your rights (GDPR / CCPA)</h2>
                <ul>
                    <li>
                        <strong>Access &amp; export</strong>: download a portable copy from
                        Settings → Export my data.
                    </li>
                    <li>
                        <strong>Deletion</strong>: Settings → Delete my account. We process
                        within 30 days.
                    </li>
                    <li>
                        <strong>Correction</strong>: edit your profile, or contact us.
                    </li>
                    <li>
                        <strong>Withdraw consent</strong>: Settings → consent toggles.
                    </li>
                </ul>

                <h2>Children</h2>
                <p>
                    Clipsmith is not intended for children under 13 (under 16 in the EEA).
                    We block sign-ups below that age and delete on discovery.
                </p>

                <h2>Retention</h2>
                <p>
                    Active account: data retained while account exists. Deleted accounts:
                    purged within 30 days, except where law requires longer (e.g. tax,
                    fraud investigations).
                </p>

                <h2>Contact</h2>
                <p>
                    Privacy questions: <Link href="mailto:privacy@clipsmith.app" className="underline">privacy@clipsmith.app</Link>
                </p>
            </article>
        </div>
    );
}
