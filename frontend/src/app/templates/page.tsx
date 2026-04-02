'use client';

import { Suspense } from 'react';
import { Loader2 } from 'lucide-react';
import { TemplateBrowser } from "@/components/templates/template-browser";

function TemplatesLoading() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <p className="text-sm text-zinc-500">Loading templates...</p>
      </div>
    </div>
  );
}

export default function TemplatesPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <Suspense fallback={<TemplatesLoading />}>
        <TemplateBrowser />
      </Suspense>
    </div>
  );
}
