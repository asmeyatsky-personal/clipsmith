'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api/client';

function VerifyInner() {
    const params = useSearchParams();
    const router = useRouter();
    const token = params.get('token') ?? '';
    const [status, setStatus] = useState<'loading' | 'ok' | 'err'>('loading');
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (!token) {
            setStatus('err');
            setMessage('No verification token provided.');
            return;
        }
        (async () => {
            try {
                await apiClient(`/auth/verify-email/${encodeURIComponent(token)}`, {
                    method: 'POST',
                });
                setStatus('ok');
                setMessage('Your email has been verified.');
                setTimeout(() => router.push('/feed'), 1500);
            } catch (e) {
                setStatus('err');
                setMessage(
                    e instanceof Error ? e.message : 'Verification failed',
                );
            }
        })();
    }, [token, router]);

    return (
        <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-zinc-950 text-white p-6">
            {status === 'loading' && (
                <>
                    <Loader2 className="w-12 h-12 animate-spin text-blue-500" />
                    <p>Verifying…</p>
                </>
            )}
            {status === 'ok' && (
                <>
                    <CheckCircle2 className="w-12 h-12 text-green-500" />
                    <p>{message}</p>
                </>
            )}
            {status === 'err' && (
                <>
                    <AlertCircle className="w-12 h-12 text-red-500" />
                    <p>{message}</p>
                    <Link
                        href="/login"
                        className="px-6 py-2 rounded-full bg-blue-500 mt-2"
                    >
                        Back to login
                    </Link>
                </>
            )}
        </div>
    );
}

export default function VerifyEmailPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-zinc-950" />}>
            <VerifyInner />
        </Suspense>
    );
}
