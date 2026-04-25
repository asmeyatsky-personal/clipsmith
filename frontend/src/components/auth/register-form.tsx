'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api/client';
import Link from 'next/link';

export function RegisterForm() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        date_of_birth: '',
    });
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        // Defense-in-depth: client-side age check (server is the source of truth).
        if (!formData.date_of_birth) {
            setError('Please provide your date of birth');
            return;
        }
        const dob = new Date(formData.date_of_birth);
        const today = new Date();
        let age = today.getFullYear() - dob.getFullYear();
        const m = today.getMonth() - dob.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
        if (age < 13) {
            setError('You must be at least 13 to use Clipsmith.');
            return;
        }
        try {
            await apiClient('/auth/register', {
                method: 'POST',
                body: JSON.stringify(formData),
                credentials: 'include',
            });
            router.push('/login');
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Registration failed');
        }
    };

    return (
        <div className="max-w-md w-full mx-auto p-8 rounded-2xl bg-white shadow-xl border border-gray-100 dark:bg-zinc-900 dark:border-zinc-800">
            <h2 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
                Join clipsmith
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
                {error && <div className="p-3 bg-red-50 text-red-500 rounded-lg text-sm">{error}</div>}

                <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Username</label>
                    <input
                        type="text"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all dark:bg-zinc-800 dark:border-zinc-700"
                        value={formData.username}
                        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                        required
                    />
                </div>

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
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Password</label>
                    <input
                        type="password"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all dark:bg-zinc-800 dark:border-zinc-700"
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                        Date of birth
                    </label>
                    <input
                        type="date"
                        max={new Date().toISOString().split('T')[0]}
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all dark:bg-zinc-800 dark:border-zinc-700"
                        value={formData.date_of_birth}
                        onChange={(e) =>
                            setFormData({ ...formData, date_of_birth: e.target.value })
                        }
                        required
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        You must be at least 13 to sign up.
                    </p>
                </div>

                <p className="text-xs text-gray-500">
                    By creating an account you agree to our{' '}
                    <Link href="/legal/terms" className="underline">
                        Terms
                    </Link>{' '}
                    and{' '}
                    <Link href="/legal/privacy" className="underline">
                        Privacy Policy
                    </Link>
                    .
                </p>

                <button
                    type="submit"
                    className="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-semibold shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all"
                >
                    Create Account
                </button>
            </form>

            <p className="mt-6 text-center text-sm text-gray-500">
                Already have an account?{' '}
                <Link href="/login" className="text-blue-600 hover:underline">
                    Sign in
                </Link>
            </p>
        </div>
    );
}
