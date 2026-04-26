// Production-suppressed logger. The bundler tree-shakes the no-ops in
// release builds (NODE_ENV=production); during dev these still surface
// in the browser console.
const isDev =
    typeof process !== 'undefined' && process.env.NODE_ENV !== 'production';

type Args = unknown[];

export const log = {
    debug: (...args: Args) => {
        if (isDev) console.debug(...args);
    },
    info: (...args: Args) => {
        if (isDev) console.info(...args);
    },
    warn: (...args: Args) => {
        if (isDev) console.warn(...args);
    },
    // Errors stay on in production — Sentry hooks the global handler.
    error: (...args: Args) => {
        console.error(...args);
    },
};
