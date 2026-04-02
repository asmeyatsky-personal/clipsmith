'use client';

import { Suspense } from 'react';
import { Loader2 } from 'lucide-react';
import { EditorApp } from '@/components/editor/editor-app';

function EditorLoading() {
    return (
        <div className="flex items-center justify-center min-h-[60vh]">
            <div className="flex flex-col items-center gap-3">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                <p className="text-sm text-zinc-500">Loading editor...</p>
            </div>
        </div>
    );
}

export default function EditorPage() {
    return (
        <Suspense fallback={<EditorLoading />}>
            <EditorApp />
        </Suspense>
    );
}
