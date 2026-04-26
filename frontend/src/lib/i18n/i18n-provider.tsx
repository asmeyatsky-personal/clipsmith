'use client';

import { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import { LOCALES, MESSAGES, type Locale, type MessageKey } from './messages';

type I18nContextValue = {
    locale: Locale;
    setLocale: (l: Locale) => void;
    t: (key: MessageKey) => string;
};

const I18nContext = createContext<I18nContextValue | null>(null);

const STORAGE_KEY = 'clipsmith.locale';

function detectLocale(): Locale {
    if (typeof window === 'undefined') return 'en';
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && (LOCALES as readonly string[]).includes(stored)) {
        return stored as Locale;
    }
    const nav = window.navigator.language?.slice(0, 2).toLowerCase();
    return ((LOCALES as readonly string[]).includes(nav) ? nav : 'en') as Locale;
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
    const [locale, setLocaleState] = useState<Locale>('en');

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setLocaleState(detectLocale());
    }, []);

    const setLocale = useCallback((l: Locale) => {
        setLocaleState(l);
        if (typeof window !== 'undefined') {
            window.localStorage.setItem(STORAGE_KEY, l);
            document.documentElement.lang = l;
        }
    }, []);

    const t = useCallback(
        (key: MessageKey): string => MESSAGES[locale][key] ?? MESSAGES.en[key] ?? key,
        [locale],
    );

    const value = useMemo(() => ({ locale, setLocale, t }), [locale, setLocale, t]);

    return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
    const ctx = useContext(I18nContext);
    if (!ctx) throw new Error('useI18n must be used inside <I18nProvider>');
    return ctx;
}
