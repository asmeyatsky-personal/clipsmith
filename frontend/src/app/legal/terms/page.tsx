'use client';

import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function TermsPage() {
    const router = useRouter();
    return (
        <div className="min-h-screen bg-zinc-950 text-white">
            <div className="flex items-center gap-3 px-4 pt-[max(env(safe-area-inset-top),12px)] pb-3 border-b border-zinc-800">
                <button onClick={() => router.back()} aria-label="Back">
                    <ArrowLeft className="w-6 h-6" />
                </button>
                <h1 className="font-semibold">Terms of Service</h1>
            </div>

            <article className="max-w-2xl mx-auto p-6 prose prose-invert prose-sm">
                <p className="text-xs text-zinc-500">Last updated: 2026-04-25</p>

                <h2>Eligibility</h2>
                <p>
                    You must be at least 13 years old (16 in the EEA, 17 to use the iOS
                    app). By creating an account you confirm you meet this requirement.
                </p>

                <h2>Your content</h2>
                <p>
                    You retain ownership of what you post. You grant Clipsmith a
                    worldwide, royalty-free license to host, transcode, distribute, and
                    display your content as part of operating the service. You are
                    responsible for the rights and clearances for everything you upload —
                    including any music, footage, or third-party material.
                </p>

                <h2>Prohibited content</h2>
                <p>
                    No: nudity / sexual content, content depicting minors in sexual
                    contexts, violence intended to incite, hate speech, harassment,
                    self-harm promotion, illegal activity, intellectual-property
                    infringement, malware, or spam. We remove violations and may suspend
                    accounts that repeatedly post them.
                </p>

                <h2>Reporting and moderation</h2>
                <p>
                    Use the report button on any post that violates these terms. We
                    review reports and take action within 24 hours where possible. We
                    combine automated detection (AI moderation) with human review.
                </p>

                <h2>Music &amp; copyright</h2>
                <p>
                    Only royalty-free or properly licensed audio is permitted. We
                    respond to valid DMCA notices. Repeat infringers will be terminated.
                </p>

                <h2>Payments</h2>
                <p>
                    On iOS, digital subscriptions and tips backed by digital goods are
                    processed via Apple In-App Purchase per Apple Guideline 3.1.1.
                    Direct cash tipping to creators is processed via Stripe.
                </p>

                <h2>Termination</h2>
                <p>
                    You can delete your account at any time from Settings. We may
                    suspend or close accounts that violate these terms or applicable law.
                </p>

                <h2>Disclaimers</h2>
                <p>
                    The service is provided &quot;as is&quot; without warranties of any kind. To
                    the maximum extent permitted by law, our liability is limited to
                    fees you have paid us in the twelve months preceding any claim.
                </p>

                <h2>Governing law &amp; disputes</h2>
                <p>
                    These terms are governed by the laws of the jurisdiction where
                    Clipsmith is incorporated. Disputes will be resolved by the courts
                    competent for that jurisdiction. EU/UK consumers retain their
                    statutory rights to bring claims locally.
                </p>

                <h2>Changes</h2>
                <p>
                    We may update these terms. Material changes will be notified in-app
                    or by email. Continued use after notification constitutes
                    acceptance.
                </p>
            </article>
        </div>
    );
}
