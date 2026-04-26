'use client';

import { useI18n } from '@/lib/i18n/i18n-provider';
import { LOCALES, LOCALE_LABELS, type Locale } from '@/lib/i18n/messages';
import { Languages } from 'lucide-react';

export function LanguageSwitcher() {
    const { locale, setLocale, t } = useI18n();
    return (
        <label className="inline-flex items-center gap-2 text-sm">
            <Languages size={16} className="text-zinc-500" />
            <span className="sr-only">{t('settings.language')}</span>
            <select
                value={locale}
                onChange={(e) => setLocale(e.target.value as Locale)}
                className="bg-transparent border border-zinc-300 dark:border-zinc-700 rounded-md px-2 py-1"
                aria-label={t('settings.language')}
            >
                {LOCALES.map((l) => (
                    <option key={l} value={l}>
                        {LOCALE_LABELS[l]}
                    </option>
                ))}
            </select>
        </label>
    );
}
