'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Loader2, Save } from 'lucide-react';
import { userService } from '@/lib/api/user';
import { useAuthStore } from '@/lib/auth/auth-store';

export default function EditProfilePage() {
    const router = useRouter();
    const { user, fetchCurrentUser } = useAuthStore();
    const [bio, setBio] = useState('');
    const [avatarUrl, setAvatarUrl] = useState('');
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (!user) return;
        // Pre-fill from current /auth/me response
        userService.getProfile(user.username).then((p) => {
            setBio((p.user as { bio?: string }).bio ?? '');
            setAvatarUrl((p.user as { avatar_url?: string }).avatar_url ?? '');
        }).catch(() => {});
    }, [user]);

    const save = async () => {
        setSaving(true);
        setError(null);
        setSuccess(false);
        try {
            await userService.updateProfile({
                bio,
                avatar_url: avatarUrl || null,
            });
            setSuccess(true);
            await fetchCurrentUser();
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Save failed');
        } finally {
            setSaving(false);
        }
    };

    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-white">
                <p>Log in to edit your profile</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-950 text-white">
            <div className="flex items-center gap-3 px-4 pt-[max(env(safe-area-inset-top),12px)] pb-3 border-b border-zinc-800">
                <button onClick={() => router.back()} aria-label="Back">
                    <ArrowLeft className="w-6 h-6" />
                </button>
                <h1 className="font-semibold">Edit profile</h1>
            </div>

            <div className="max-w-md mx-auto p-4 space-y-4">
                <div>
                    <label className="block text-xs text-zinc-500 mb-1">Username</label>
                    <input
                        readOnly
                        value={user.username}
                        className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-500"
                    />
                </div>

                <div>
                    <label className="block text-xs text-zinc-500 mb-1">Bio</label>
                    <textarea
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        maxLength={500}
                        rows={4}
                        placeholder="Tell people about yourself"
                        className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-800 resize-none"
                    />
                    <div className="text-xs text-zinc-600 text-right mt-1">{bio.length}/500</div>
                </div>

                <div>
                    <label className="block text-xs text-zinc-500 mb-1">Avatar URL</label>
                    <input
                        value={avatarUrl}
                        onChange={(e) => setAvatarUrl(e.target.value)}
                        placeholder="https://..."
                        className="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-800"
                    />
                    <p className="text-xs text-zinc-600 mt-1">
                        Direct image URL. Native upload coming soon.
                    </p>
                </div>

                {error && <p className="text-sm text-red-400">{error}</p>}
                {success && <p className="text-sm text-green-400">Saved.</p>}

                <button
                    onClick={save}
                    disabled={saving}
                    className="w-full py-3 rounded-full bg-blue-500 hover:bg-blue-600 disabled:opacity-50 flex items-center justify-center gap-2 font-semibold"
                >
                    {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
                    Save
                </button>
            </div>
        </div>
    );
}
