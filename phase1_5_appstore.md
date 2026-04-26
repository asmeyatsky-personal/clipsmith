# Phase 1.5 — TestFlight + App Store submission plan

**Status:** plan only. Do not execute without explicit go-ahead.
**Audience:** solo bootstrapping founder, ~3 calendar weeks, code already complete.
**Goal:** First public TestFlight build, then one App Review submission for production.

---

## 0. Pre-conditions (must be true before starting)

- [ ] Apple Developer Program enrollment ($99/yr) — **2-day minimum lead time**
- [ ] D-U-N-S number for the entity that will own the app (free, ~24h via Apple's request flow)
- [ ] Mac with current Xcode (at least 15.x) and a paid Apple ID added in Xcode → Settings → Accounts
- [ ] Production backend reachable on a stable HTTPS URL (Neon Postgres + a deployed FastAPI; Cloudflare or Fly.io is fine)
- [ ] Stripe live keys + Connect onboarding URL ready (tipping payouts)
- [ ] Sentry DSN configured for the iOS-shell webview to report unhandled errors
- [ ] Domain `clipsmith.app` (or whatever) resolved with valid TLS — used for universal links
- [ ] Privacy policy + Terms of Use pages live and reachable from the web (already have `/legal/privacy` + `/legal/terms`; just confirm they are deployed)

If any of those are missing, fix them before opening Xcode.

---

## 1. App Store Connect setup (Day 1–2, ~half a day in browser)

1. Create the app record in App Store Connect (bundle id `app.clipsmith`, primary language `en-US`).
2. Reserve a unique **App Name** (you only get one shot at the name, and it has to be globally unique on the store).
3. **App Privacy questionnaire** — declare every data type the app collects. Match it 1:1 with `PrivacyInfo.xcprivacy` already in the bundle and our backend reality:
   - Account info (email, username) → linked to identity, used for app functionality
   - Crash + diagnostic data (Sentry) → not linked to identity
   - Usage data (views, likes) → linked to identity, used for personalisation
   - Audio / Video / Photos → for upload feature, linked, used for app functionality
   - Camera / Microphone (live record) → linked, used for app functionality
4. Subscriptions + IAP: create **at minimum** one auto-renewable subscription group with three tiers ($1.99/$4.99/$9.99) and one consumable for super-tips. Each needs a localised display name + description in EN. Apple ties these to App Review — don't ship without them.
5. **Age rating** questionnaire. UGC + chat → expect "17+" with "Frequent/Intense Mature/Suggestive Themes" once Apple sees user-generated chat. Do not lie here; rejection-fast.
6. Pre-create app categories: Primary `Photo & Video`, Secondary `Social Networking`.

**Cost:** $0 today (the $99 is already paid).
**Risk:** App name collision is the biggest day-1 surprise. Have 3 backup names.

---

## 2. Native iOS plumbing (Day 3–7)

The Capacitor shell is built (`frontend/ios/App`). What needs work is the surrounding native config + native plugin entitlements.

### 2.1. Bundle + signing

- [ ] Create an App ID in Apple Developer portal with `app.clipsmith`, enable: Push Notifications, Sign in with Apple, Associated Domains, In-App Purchase.
- [ ] Create an iOS Distribution certificate (managed by Xcode "Automatically manage signing" is acceptable for solo).
- [ ] Create one Development + one App Store provisioning profile.
- [ ] Add an `Associated Domains` entitlement: `applinks:clipsmith.app` so a tap on a `https://clipsmith.app/v/<id>` link opens the app.
- [ ] Push entitlement (`aps-environment`: `production` for App Store builds).

### 2.2. Info.plist usage strings (mandatory — Apple rejects without)

These have to be human-readable and accurate. Place in `frontend/ios/App/App/Info.plist`:

```
NSCameraUsageDescription           = "Clipsmith uses the camera so you can record videos and go live."
NSMicrophoneUsageDescription       = "Clipsmith uses the microphone so your videos and live streams have audio."
NSPhotoLibraryAddUsageDescription  = "Clipsmith saves clips you export to your camera roll."
NSPhotoLibraryUsageDescription     = "Clipsmith uses your photo library to upload existing videos."
NSUserTrackingUsageDescription     = "Clipsmith uses this only for crash analytics; no advertising tracking."
```

### 2.3. App icons + launch screen

- [ ] Generate `Assets.xcassets/AppIcon.appiconset/` from a single 1024×1024 PNG via `cordova-res` or `capacitor-assets`. Apple now also needs the new tinted/dark variants for iOS 18.
- [ ] Replace the default launch screen with one that matches the splash brand colour (currently `#000000` in `capacitor.config.ts`).

### 2.4. Native plugins to verify

The repo already declares `@capacitor/push-notifications` and (presumably) some camera/photos plugins. Re-test each on a physical device, not just a simulator, since the simulator doesn't fire push tokens or expose the real microphone:

- [ ] PushNotifications.register() actually POSTs the device token to `/push/register-token`
- [ ] CapacitorVideoPlayer (or whichever native video plugin) plays HLS not just MP4 (your CDN may serve HLS once you wire Cloudflare Stream)
- [ ] Camera + photo library round-trip into `/api/videos/upload`

### 2.5. App Tracking Transparency

Even though we don't track for ads, Apple wants `NSUserTrackingUsageDescription` declared the moment IDFA is touched by any SDK. Sentry sometimes pulls IDFA depending on its iOS SDK version — verify and otherwise leave this string in.

### 2.6. Apple IAP wiring

- [ ] Add `@capacitor-community/in-app-purchases-2` (or RevenueCat — strongly recommended for solo, ~$0/mo until $10k MRR).
- [ ] Wire purchase flow → backend `/api/payments/iap-receipt` endpoint that validates the receipt against Apple's verifyReceipt server, then upserts a `SubscriptionDB` row.
- [ ] Sandbox test on TestFlight with a Sandbox Apple ID before promoting.

**Apple Guideline gotcha (Phase 3 plan §5 already flagged this):**
- Subscriptions and digital goods → MUST use Apple IAP (Stripe disallowed, 30% rev share).
- Cash tipping to identifiable humans → Stripe Connect is allowed.
- Brand-deal payouts to creators → Stripe is allowed (B2B-ish, not digital goods).
- Mark UI accordingly so reviewer can see at a glance which path each button uses.

---

## 3. Build, sign, upload (Day 8–9)

```bash
cd frontend
npm run build            # static export → out/
npx cap sync ios         # copy out/ → ios/App/App/public
xcodebuild archive ...   # or do it in Xcode UI
```

- [ ] Bump `MARKETING_VERSION` and `CURRENT_PROJECT_VERSION` (Info.plist) every upload.
- [ ] Archive → "Distribute App" → "App Store Connect" → upload.
- [ ] Wait ~10–30 min for Apple's automated processing.
- [ ] Add the build to the **TestFlight Internal Testing** group (just you and any TestFlight-eligible accounts you control — this skips Beta App Review).

If processing fails: check the email Apple sends. Common: missing privacy strings, missing 1024×1024 icon, ITMS-90096 (architecture warnings).

---

## 4. TestFlight beta (Day 10–14)

1. Internal testing first — add up to 100 internal testers (no Apple review).
2. Walk through every PRD-promised feature at least once on a real device:
   - Sign up + email verify
   - Upload + scene-detect + caption + voice-enhance
   - Feed scroll, like, comment, follow
   - Live record, BG-removal, multi-track editor
   - Subscribe (sandbox IAP), tip (Stripe sandbox), premium-gated content
   - Watch party WS sync (open on two devices)
   - Duet (verify FFmpeg job actually completes server-side)
3. Add 2–5 trusted external testers (separate group, **does** require Apple Beta App Review — usually 24h, sometimes 3 days).
4. Collect TestFlight feedback (in-app screenshot tool) for ~5 days. Fix critical bugs only — don't scope-creep.
5. **Track every crash** in Sentry. Apple looks at TestFlight crash rate when reviewing v1.

---

## 5. Pre-submission checklist (Day 15–16)

Make sure each of these is genuinely true before hitting Submit:

- [ ] App icon + launch screen polished, no placeholder Capacitor bird
- [ ] All Info.plist usage strings in place AND meaningful
- [ ] No crashes on iPhone SE (smallest current screen) and iPhone 15 Pro Max
- [ ] Login + sign-up flow has Sign in with Apple as an option (mandatory if any other 3rd-party login is offered — we don't currently have 3rd-party, so technically optional, but adding it now avoids a future rejection)
- [ ] **Account deletion is reachable in-app** (not just on the web). Settings → Delete account → existing GDPR endpoint. Apple rejects without this since 2022.
- [ ] Reporting + blocking flow is reachable on every UGC surface (videos, comments, profiles, DMs). Already have endpoints; verify UI exposes them.
- [ ] Content moderation pipeline is live (OpenAI text moderation already wired). For day-1 launch consider also having a manual upload-cap (existing risk §2 in plan).
- [ ] Privacy policy + Terms reachable from in-app Settings, not just the web.
- [ ] All marketing copy on the App Store page matches what the app actually does. UGC apps get audited harder.
- [ ] Demo account credentials prepared for the reviewer (App Store Connect → App Review Information → Demo Account). Pre-populate it with a few uploads + a few followers.
- [ ] App Review notes mention specifically:
  - Tipping uses Stripe (B2B); subscriptions use Apple IAP. Reviewer will check.
  - Live streaming uses our own SFU (not WebRTC peer-to-peer that bypasses Apple).
  - Music in user uploads is **royalty-free only** (the strategy from §10.1) — link to the in-app library.

### Screenshots

Apple now requires only the 6.9" iPhone size (1320×2868) and 13" iPad if you support iPad. Avoid the iPad submission for v1 — declare iPhone-only in App Store Connect → App Information → "iPad" toggle off. Saves a whole rejection vector.

Take **8 screenshots** showing real screens (no marketing mock-ups):
1. Feed scrolling
2. Video player with engagement bar
3. Recording screen with BG removal toggle
4. Multi-track editor mid-edit
5. AI captions overlay on a clip
6. Profile + following list
7. Subscribe-to-creator paywall
8. Community group thread

---

## 6. Submit (Day 17)

- Pick a release type: **Manual release after approval** (lets you co-ordinate marketing on the day-of).
- Submit for App Review.
- Apple median review time: ~24h. UGC + payments adds variance — budget up to **5 days**.
- Watch your email + App Store Connect "Resolution Center" obsessively.

### Most likely rejection reasons + plan

| Likely rejection (Apple guideline) | Mitigation already in place | If they still flag it |
|---|---|---|
| 1.2 — Safety, UGC | Reporting + blocking + moderation already wired | Add a contact email + 24h response SLA in App Review notes |
| 4.2.3 — Min functionality (UGC + content) | Pre-seed demo account with curated content | Record a 30s screen capture of the app in use, attach to Resolution Center reply |
| 5.1.1 — Privacy + account deletion | GDPR delete reachable in-app | Send the reviewer the exact in-app path |
| 3.1.1 — IAP routing | Stripe only on tipping/brand-deals; subscriptions on IAP | Re-explain in writing, point to specific buttons |
| Screenshot mismatch | Use real screens | Re-shoot, re-upload — fast iteration |

Each rejection round usually adds 24–48h. **Budget 2–3 rounds.**

---

## 7. Post-approval (Day 18+)

- [ ] Manually release.
- [ ] Set up RC observability: Sentry release tags per build, Cloudflare RUM on the hosted site.
- [ ] Monitor App Store ratings/reviews daily for the first week.
- [ ] Have a hotfix branch ready: any crash > 0.5% session means same-day patch.

---

## 8. Costs (cash + time)

| Item | Cash | Time |
|---|---|---|
| Apple Developer Program | $99/yr | — |
| D-U-N-S | $0 | 1 day wait |
| Sentry (free tier) | $0 | — |
| Cloudflare Stream / Bunny (recommend Bunny for solo, $1/1k mins) | ~$10–30/mo | — |
| RevenueCat (free up to $10k MRR) | $0 | — |
| Total Phase 1.5 cash | ~$100 | ~3 weeks calendar |

---

## 9. What is explicitly **out of scope** for Phase 1.5

- Mediasoup VPS (live streaming runs against the placeholder adapter; gate the live UI behind a feature flag for v1)
- BigQuery analytics export (JSONL placeholder is fine for v1)
- Localized App Store listings (EN-only at launch; the in-app i18n shipped in Phase 6 still works)
- Music licensing deal with a real label (royalty-free libraries only, per §10.1)
- External pen test (do once DAU > 1k, or after first dust-up)
- Rust hot-path migration (only if measured p99 > 50ms)

These are explicitly Phase 7+ when there is real usage data to justify the cost.

---

## 10. Decisions you'll need from the founder during Phase 1.5

1. App display name — final pick + 2 fallbacks.
2. Subscription price points — confirm $1.99 / $4.99 / $9.99 or change.
3. App-Store category — confirm Photo & Video / Social Networking.
4. Domain — final `.app` / `.com` choice for universal links.
5. Marketing-day plan — pre-launch waitlist? launch on Product Hunt? pure stealth? affects review notes (Apple looks at marketing claims).
