'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth/auth-store';
import { apiClient } from '@/lib/api/client';
import Link from 'next/link';

export function LoginForm() {
    const router = useRouter();
    const setAuth = useAuthStore((state) => state.setAuth);
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
                credentials: 'include',
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            setAuth(data.user);
            router.push('/');
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Login failed');
        }
    };

    return (
        <div className="max-w-md w-full mx-auto p-8 rounded-2xl bg-white shadow-xl border border-gray-100 dark:bg-zinc-900 dark:border-zinc-800">
            <h2 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
                Welcome Back
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
                {error && <div className="p-3 bg-red-50 text-red-500 rounded-lg text-sm">{error}</div>}

                <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Email</label>
                    <input
                        type="email"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all dark:bg-zinc-800 dark:border-zinc-700"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        required
                    />
                </div>

                <div>
                    <div className="flex justify-between items-center mb-2">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
                        <Link href="/forgot-password" className="text-sm text-blue-600 hover:underline">
                            Forgot password?
                        </Link>
                    </div>
                    <input
                        type="password"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all dark:bg-zinc-800 dark:border-zinc-700"
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        required
                    />
                </div>

                <button
                    type="submit"
                    className="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-semibold shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all"
                >
                    Sign In
                </button>
            </form>

            <div className="mt-4 flex items-center gap-3">
                <div className="h-px flex-1 bg-zinc-200 dark:bg-zinc-700" />
                <span className="text-xs text-zinc-500">or</span>
                <div className="h-px flex-1 bg-zinc-200 dark:bg-zinc-700" />
            </div>

            <button
                type="button"
                aria-label="Continue with Apple"
                onClick={() => {
                    window.location.href = '/auth/apple/start';
                }}
                className="mt-3 w-full py-3 rounded-xl bg-black text-white font-medium flex items-center justify-center gap-2 hover:bg-zinc-800 transition-all"
            >
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">
                    <path d="M16.365 1.43c0 1.14-.46 2.21-1.21 2.97-.81.81-2.13 1.43-3.18 1.35-.13-1.13.45-2.3 1.18-3.04.81-.83 2.18-1.46 3.21-1.28zM20.94 17.78c-.61 1.36-.91 1.97-1.7 3.18-1.1 1.69-2.66 3.79-4.59 3.81-1.71.02-2.16-1.12-4.49-1.11-2.34.02-2.83 1.13-4.55 1.11-1.93-.02-3.4-1.91-4.51-3.6C-.36 17.7-.55 11.86 1.66 8.82c1.57-2.16 4.04-3.42 6.36-3.42 2.36 0 3.84 1.29 5.78 1.29 1.89 0 3.04-1.29 5.77-1.29 2.06 0 4.24 1.12 5.79 3.06-5.09 2.79-4.26 10.07-1.42 9.32z"/>
                </svg>
                Continue with Apple
            </button>

            <p className="mt-6 text-center text-sm text-gray-500">
                Don&apos;t have an account?{' '}
                <Link href="/register" className="text-blue-600 hover:underline">
                    Create one
                </Link>
            </p>
        </div>
    );
}
