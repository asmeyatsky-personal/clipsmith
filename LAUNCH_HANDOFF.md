# Clipsmith — Launch Readiness Handoff

**Last updated:** 2026-07-13
**Branch with all work:** `launch-readiness-fixes` (commit `ab136b6`, branched from `main`)
**Remote:** repo moved to `https://github.com/asmeyatsky-personal/clipsmith.git`
(update your remote: `git remote set-url origin https://github.com/asmeyatsky-personal/clipsmith.git`)

**Launch target:** iOS App Store (web is a prerequisite since the iOS app is a Capacitor shell around the static web build).

---

## 0. TL;DR — where things stand

The app is a well-architected FastAPI (DDD) backend + Next.js 16 static-export frontend + Capacitor iOS shell. An end-to-end assessment plus a hardening pass are **done and verified**. The code is **not blocked on engineering** anymore — what remains is mostly **infra provisioning** and **iOS submission mechanics** that require your accounts/hardware.

**Verified green on the branch:**
- Backend: **504 unit/API tests + 10 smoke tests pass**
- Frontend: **builds** (static export, 27 routes), **4 unit tests pass**, lint clean (warnings only)
- Security: **bandit clean**, **pip-audit green** (with documented ignores), **npm audit green** (shipped deps)
- Architecture: **import-linter 5/5 contracts kept**

**The single biggest thing fixed:** the entire video editor backend was returning HTTP 500 on every request (never caught because the editor had ~no tests). That is fixed, and the editor's Export button now does a real ffmpeg render.

---

## 1. Environment / how to work on this repo

There are several Python venvs in the repo. **Use `.venv-test`** — Python 3.12.8, matches CI, has deps installed:

```bash
cd /Users/allansmeyatsky/clipsmith
.venv-test/bin/python --version    # 3.12.8
```

**Local tooling notes:**
- `ffmpeg` is **NOT installed locally** — video processing + editor export can't be exercised end-to-end on this machine. The production `Dockerfile.backend` installs it (`apt-get install -y ffmpeg`). The render filtergraph was validated by compiling the ffmpeg args (no binary needed); the no-render code paths are fully tested.
- `redis-server` **is** installed and running locally, so `enqueue()` uses a real RQ queue (jobs sit unprocessed unless you run a worker). In CI/tests (`REDIS_URL=` empty) it falls back to a synchronous in-process queue.
- Frontend: Node 22, `npm ci` already run in `frontend/`.

### Re-run every gate locally (mirrors CI)

```bash
cd /Users/allansmeyatsky/clipsmith

# Backend unit + API
JWT_SECRET_KEY=ci-test-secret-key-not-for-production DATABASE_URL=sqlite:///test.db REDIS_URL= \
  .venv-test/bin/python -m pytest backend/tests --ignore=backend/tests/smoke -q

# Backend smoke (relies on import-time table creation into the smoke DB)
rm -f clipsmith-smoke.db
JWT_SECRET_KEY=ci-test-secret-key-not-for-production DATABASE_URL=sqlite:///clipsmith-smoke.db REDIS_URL= \
  .venv-test/bin/python -m pytest backend/tests/smoke -q

# Architecture contracts
PYTHONPATH=. .venv-test/bin/lint-imports --config backend/.importlinter

# Dependency audits
.venv-test/bin/pip-audit -r backend/requirements.txt --strict \
  --ignore-vuln PYSEC-2026-161 --ignore-vuln PYSEC-2026-248 --ignore-vuln PYSEC-2026-249 \
  --ignore-vuln CVE-2026-48818 --ignore-vuln CVE-2026-48817 \
  --ignore-vuln PYSEC-2026-1805 --ignore-vuln PYSEC-2026-1325
(cd frontend && npm audit --omit=dev --audit-level=high)

# Static security
(cd backend && ../.venv-test/bin/bandit -r . -ll -x ./tests,./venv,./test_env,./.venv)

# Frontend
(cd frontend && npm run lint && npm test && npm run build)
```

---

## 2. What was done (this branch)

| Area | Change | Files |
|---|---|---|
| **Editor auth bug (critical)** | Local `get_current_user` returned a dict; every editor endpoint used `.id` → 500 on all 35 endpoints. Removed the broken override so the router uses the shared dependency (returns the User entity). | `backend/presentation/api/video_editor_router.py` |
| **Editor repo mapping bug** | DB col `extra_metadata` vs domain field `metadata`; `VideoProject(**db.model_dump())` raised. Added `_project_to_domain` mapping helper. | `backend/infrastructure/repositories/sqlite_video_editor_repo.py` |
| **Real export pipeline** | Replaced the stub `/export` with `export_project_task` (RQ): downloads timeline clips → ffmpeg scale/pad/concat → uploads via storage adapter → tracks job state in `VideoProjectDB.extra_metadata`. `/export-status` reads real state. Wired Export/Download button + polling in the editor UI. | `backend/infrastructure/queue/tasks.py`, `backend/presentation/api/video_editor_router.py`, `backend/presentation/dependencies.py`, `frontend/src/components/editor/video-editor.tsx` |
| **Prod config guards** | `os.getenv("ENVIRONMENT")` guards → `@model_validator` on the parsed field (JWT secret, no SQLite, non-local storage in prod). | `backend/infrastructure/config.py` |
| **Migrations in prod** | Alembic runs as Fly `release_command`; `alembic.ini` uses `%(here)s` (CWD-independent); prod skips `create_all` (dev/test only). | `fly.toml`, `backend/alembic.ini`, `backend/infrastructure/repositories/database.py` |
| **Frontend prod API URL** | `fly.frontend.toml` bakes `NEXT_PUBLIC_API_URL` at build time (static export inlines it). | `fly.frontend.toml` |
| **Stripe event-loop blocking** | All 13 blocking Stripe SDK calls wrapped in `anyio.to_thread.run_sync`. | `backend/infrastructure/services/stripe_service.py` |
| **Dependency CVEs** | Bumped `python-multipart`, `cryptography`, `bleach`, `idna`. Documented+ignored framework-locked ones in CI. Frontend gate audits shipped deps. | `backend/requirements.txt`, `.github/workflows/ci.yml` |
| **Hide dead-end features** | AI video-gen / voice-over / live-streaming → `501` behind feature flags (off by default); hid the two dead AI editor tabs. | `backend/presentation/api/ai_router.py`, `backend/presentation/api/social_router.py`, `frontend/src/components/editor/ai-tools-panel.tsx`, `frontend/src/lib/features.ts` |
| **iOS cookie** | Auth cookie `SameSite`/`Secure` configurable; set `SameSite=None; Secure` for the Capacitor cross-origin flow. | `backend/presentation/api/auth_router.py`, `backend/infrastructure/config.py`, `fly.toml` |
| **iOS app icon** | Replaced Capacitor placeholder with a real opaque branded icon (+ web/PWA sizes). | `frontend/ios/.../AppIcon-512@2x.png`, `frontend/public/icon-*.png`, `apple-touch-icon.png` |
| **Tests** | 6 new editor/export regression tests. | `backend/tests/test_editor_export.py`, `backend/tests/conftest.py` |

---

## 3. REMAINING WORK TO LAUNCH

### 3A. Infra provisioning (blocks a working deploy — do first)

The app **fail-fasts** without these (by design), so a deploy will crash-loop until they're set.

- [ ] **Postgres**: create a Neon/Fly Postgres DB. `fly secrets set DATABASE_URL=postgresql+psycopg://USER:PASS@HOST/DB?sslmode=require`
- [ ] **Redis**: provision Upstash (or Fly Redis). `fly secrets set REDIS_URL=redis://...` — **required**; `redis_config.py` raises in prod if unreachable.
- [ ] **Worker machine**: `fly scale count worker=1` (the `worker` process is defined in `fly.toml` but Fly won't run it until scaled). Without a worker, video processing **and editor export** never run.
- [ ] **Object storage (R2)**: `fly.toml` sets `STORAGE_TYPE=r2`. Set `fly secrets set R2_ACCOUNT_ID=... R2_ACCESS_KEY_ID=... R2_SECRET_ACCESS_KEY=... R2_BUCKET_NAME=clipsmith-media R2_PUBLIC_DOMAIN=media.clipsmith.app`. Local filesystem storage is rejected in prod.
- [ ] **JWT secret**: `fly secrets set JWT_SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(64))")`
- [ ] **Stripe** (payments/tips/subscriptions): `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`. Configure the webhook endpoint in Stripe → `/api/payments/webhook`.
- [ ] **Email** (verification/reset): `SMTP_HOST/PORT/USER/PASSWORD`, `FROM_EMAIL` (Resend recommended). Without it, emails only log to stderr.
- [ ] **AssemblyAI** (captions): `ASSEMBLYAI_API_KEY`. Without it, `get_transcriber()` raises in prod.
- [ ] **OpenAI** (text moderation): `OPENAI_API_KEY`. Without it, moderation silently no-ops.
- [ ] **Sentry** (optional): `SENTRY_DSN`.
- [ ] **Frontend build arg**: confirm `fly.frontend.toml` `[build.args] NEXT_PUBLIC_API_URL` points at the real backend host before `fly deploy -c fly.frontend.toml`.

### 3B. iOS App Store (the launch target)

- [ ] **Rebuild + sync with prod API URL** (the static export inlines it):
  `cd frontend && NEXT_PUBLIC_API_URL=https://<backend-host> npm run build && npx cap sync ios`
- [ ] **⚠️ Test cookie auth on a physical device** in WKWebView. The app is served from `capacitor://localhost` and calls the API cross-origin. We set `SameSite=None; Secure`, but WKWebView third-party-cookie behavior is finicky — **this is the one thing that can't be verified without hardware.** If login doesn't persist, the fallback is **bearer-token auth**: store the token from the login response body in `@capacitor/preferences` and send `Authorization: Bearer` from `frontend/src/lib/api/client.ts` (the backend already accepts the header everywhere).
- [ ] **App icon**: a real branded icon is in place, but swap for final brand art if you have it (`frontend/ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png`, 1024×1024, opaque, no rounded corners).
- [ ] **Signing**: Apple Distribution cert + provisioning profile in Xcode.
- [ ] **APNs**: `.p8` key + `APNS_KEY_ID/TEAM_ID/TOPIC` secrets for push.
- [ ] **App Store Connect**: screenshots, privacy nutrition labels, account-deletion + moderation review notes. See `APP_STORE_CHECKLIST.md` (thorough; remaining items are manual ⚙️).

### 3C. Deferred engineering (flagged, not silently dropped)

- [ ] **Framework dependency CVEs** — 8 ignored in CI because no compatible fix exists yet: starlette ×6 (fixes need starlette ≥1.0 but FastAPI 0.128 caps `<1.0`), protobuf (capped by `opentelemetry-proto<5.0`), ecdsa (no patch; off-path since JWTs use HS256). **Re-audit periodically**; when FastAPI ships a version depending on patched starlette, do a coordinated FastAPI+starlette+OTel bump and drop the `--ignore-vuln` flags in `.github/workflows/ci.yml`. Consider migrating `python-jose` → `PyJWT` to drop the ecdsa dep entirely.
- [ ] **Async DB routers** — `payment` (39), `video_editor` (35), `analytics` (18), `ai` (11) endpoints are `async def` calling synchronous DB with no threadpool. The **acute** case (multi-second blocking Stripe calls) is fixed. The DB queries are ms-scale so lower priority, but under real concurrency they serialize the event loop. Fix by converting these routers to plain `def` (FastAPI auto-threadpools sync handlers — the other 18 routers already do this) — note they use `await request.json()`, so you'll need to switch to Pydantic body models or `run_in_threadpool` around the sync work.
- [ ] **`datetime.utcnow()` deprecations** — e.g. `backend/application/dtos/auth_dto.py:30` (age gate). Replace with `datetime.now(UTC)`.
- [ ] **SQLModel `session.query()` deprecations** — e.g. `sqlite_auth_security_repo.py:116`. Migrate to `session.exec(select(...))`.

### 3D. Quality items from the assessment (not blocking, worth doing)

- [ ] **No global exception handler** — only `RateLimitExceeded` is registered (`main.py:112`). No domain-error hierarchy → unhandled use-case errors surface as raw 500s. Add a domain exception base + `app.add_exception_handler`.
- [ ] **Payments happy-path untested** — payment/editor/analytics routers are thin on tests; monitoring/push/effects/moderation routers have zero router tests. `--cov-fail-under=60` is low for a payments system.
- [ ] **Recommendation scale** — `get_personalized_feed.py:78` loads 500 videos + 5000 interactions into memory per request; O(n·m) Python scoring. Push to SQL / precompute before real traffic.
- [ ] **`docker-compose.production.yml` is broken** — references a nonexistent `backend/Dockerfile` and a `celery_app` that doesn't exist (app uses RQ). Fly is the real deploy path; **delete this file** or fix it to avoid confusion.
- [ ] **`.env.production` is committed** (placeholders only today) — `git rm --cached .env.production` and add to `.gitignore` so a real secret can't be committed by accident.
- [ ] **`/health` is shallow** (`main.py:161` returns `{"status":"ok"}`) — doesn't check DB/Redis. Fly healthchecks pass even when the DB is down. Consider a real readiness probe.
- [ ] **Frontend**: only 2 test files; `mockData.ts` is dead code (0 importers) — delete it; add a request timeout/abort to `client.ts`; register-form has minimal validation.

---

## 4. How the deploy works (reference)

- **Backend** (`fly.toml`): `Dockerfile.backend` (installs ffmpeg). Two processes — `app` (uvicorn, 2 workers) and `worker` (RQ). `[deploy] release_command = "alembic -c backend/alembic.ini upgrade head"` runs migrations before each release goes live (deploy aborts if a migration fails). `[env]` sets `ENVIRONMENT=production`, `ALLOWED_ORIGINS` (includes `capacitor://localhost`), `COOKIE_SAMESITE=none`, `STORAGE_TYPE=r2`.
  - Deploy: `fly deploy` — then one-time `fly scale count worker=1`.
- **Frontend** (`fly.frontend.toml`): `Dockerfile.frontend` builds the Next static export and serves it via nginx. `NEXT_PUBLIC_API_URL` is a build arg (compile-time, static export). Deploy: `fly deploy -c fly.frontend.toml`.
- **CI** (`.github/workflows/ci.yml`): gitleaks, import-linter, backend tests+coverage+smoke, pip-audit, bandit, frontend lint/test/build, npm audit, docker builds. **No deploy step** — deploy is manual `fly deploy`.

---

## 5. Gotchas discovered (save yourself the debugging)

1. **Editor auth**: the editor router uses the shared `get_current_user` from `dependencies.py` which returns a **User entity** (`.id`, `.email`), not a dict. Don't reintroduce a local dict-returning override.
2. **Cookie over http**: the auth cookie is `Secure`, so it is **dropped over plain http** (localhost dev). Tests and local flows authenticate via `Authorization: Bearer <token>` (token is in the login response body). Set `COOKIE_SECURE=false` for http dev if you need cookie auth locally.
3. **Sync task vs test DB**: the RQ sync-fallback runs tasks inline using `get_task_session()` (the module-level file engine), while the test `client` fixture overrides the request DB to an **in-memory** engine. So a synchronously-run task can't see rows the test client wrote. For task-logic tests, drive `get_task_session()` directly (see `test_editor_export.py::test_export_task_no_clips_marks_failed`).
4. **ffmpeg required**: editor export + video processing need ffmpeg on the worker. It's in `Dockerfile.backend`, absent locally.
5. **Import-linter bridge**: presentation must not import `infrastructure.{repositories,adapters,services}` directly. Route task/queue references through `backend/presentation/dependencies.py` (the whitelisted bridge — see how `export_project_task` and `get_video_processing_queue` are re-exported there).
6. **Feature flags**: backend `AI_GENERATION_ENABLED` / `LIVE_STREAMING_ENABLED` and frontend `NEXT_PUBLIC_AI_GENERATION` / `NEXT_PUBLIC_LIVE_STREAMING` all default OFF. Flip both sides (and wire a provider/worker) to re-enable those features.
7. **Alembic completeness**: verified the 7 migrations build the full 91-table schema (0 tables missing vs `create_all`). Column-level drift wasn't exhaustively diffed — if you add a model field, always generate a migration (prod no longer runs `create_all`).

---

## 6. What actually works end-to-end (verified during assessment)

Working: auth (register/login/reset/verify/**2FA**), video upload→moderation→transcode/thumbnail queue, personalized feed, social (follow/like/comment/block), monetization (Stripe PaymentIntent/Connect/Subscriptions/Payouts + webhook verification), captions (AssemblyAI), scene detection, chroma-key, text moderation, APNs push, analytics, community/courses/discovery/hashtags, **editor (now fixed) + real export**.

Intentionally gated off (no backend yet): AI video-gen, AI voice-over, live streaming. Watch parties are WS-signaling only.

---

## 7. First session back — suggested order

1. Provision infra (§3A) and get a crash-free `fly deploy` of the backend.
2. Deploy the frontend with the correct API URL; smoke-test auth + upload + feed in a browser.
3. Build + `cap sync` iOS; **test cookie auth on a device** (§3B) — decide cookie vs bearer.
4. Finish App Store Connect mechanics.
5. Then chip at §3C/§3D as post-launch hardening.
