# App Store Submission Checklist — Clipsmith iOS

Last updated: 2026-04-25 (Phase 1.10)

This is the live checklist for submitting Clipsmith to the App Store.
Tick items as you complete them. Anything marked ⚙️ requires you to do it
in App Store Connect / Xcode UI; anything marked 🤖 is already done in
the repo.

---

## 1. Apple Developer account

- [ ] Apple Developer Program enrolled and active ($99/yr)
- [ ] Team ID known (App Store Connect → Membership)

## 2. Xcode project config (open `frontend/ios/App/App.xcodeproj`)

- [x] 🤖 `Info.plist` declares all privacy usage strings
  (camera, microphone, photo library, push)
- [x] 🤖 `Info.plist` enables remote-notification background mode
- [x] 🤖 `Info.plist` sets `ITSAppUsesNonExemptEncryption=false`
- [x] 🤖 Portrait-only orientation (matches our full-screen vertical feed)
- [x] 🤖 `PrivacyInfo.xcprivacy` privacy manifest present
- [ ] ⚙️ Set Bundle Identifier (Signing & Capabilities tab)
       → e.g. `app.clipsmith` (matches `capacitor.config.ts`)
- [ ] ⚙️ Set Marketing Version (1.0.0) and Build Number (1)
- [ ] ⚙️ Select your Apple Team in Signing & Capabilities → "Automatically
       manage signing"
- [ ] ⚙️ Add capability: Push Notifications
- [ ] ⚙️ Add capability: Background Modes → Remote notifications
- [ ] ⚙️ Set deployment target to iOS 14.0 or later

## 3. Assets

- [ ] ⚙️ App icon (1024×1024 PNG, no alpha, no rounded corners) in
       `Assets.xcassets/AppIcon.appiconset` — Capacitor pre-fills a
       placeholder; replace before submission
- [ ] ⚙️ Launch screen (`LaunchScreen.storyboard`) — currently the
       Capacitor default; can stay simple or be branded

## 4. APNs key (for push notifications)

- [ ] ⚙️ App Store Connect → Certificates, IDs & Profiles → Keys
       → New (+) → "Apple Push Notifications service" → Continue → Register
- [ ] ⚙️ Download the `.p8` key (one-time download)
- [ ] ⚙️ Note Key ID
- [ ] ⚙️ Set on backend in `backend/.env`:
       ```
       APNS_KEY_PATH=/secrets/apns_AuthKey_XXXX.p8
       APNS_KEY_ID=<Key ID>
       APNS_TEAM_ID=<your team id>
       APNS_TOPIC=app.clipsmith
       APNS_SANDBOX=false   # true while testing on sandbox builds
       ```

## 5. Cloudflare R2 (production media storage)

- [ ] ⚙️ Cloudflare account → R2 → Create bucket `clipsmith-media`
- [ ] ⚙️ R2 → Manage API tokens → Create API token
       (Object Read+Write scoped to bucket)
- [ ] ⚙️ R2 → bucket → Settings → Custom domain → connect
       `media.clipsmith.app`
- [ ] ⚙️ Set in `backend/.env`:
       ```
       STORAGE_TYPE=r2
       R2_ACCOUNT_ID=<your account id>
       R2_ACCESS_KEY_ID=<api token access key>
       R2_SECRET_ACCESS_KEY=<api token secret>
       R2_BUCKET_NAME=clipsmith-media
       R2_PUBLIC_DOMAIN=media.clipsmith.app
       ```

## 6. App Store Connect — App Record

- [ ] ⚙️ My Apps → New App → iOS → name "Clipsmith", bundle id
       `app.clipsmith`, primary language, SKU (your internal id)
- [ ] ⚙️ Pricing → Free
- [ ] ⚙️ App Privacy → declare data collection types matching
       `PrivacyInfo.xcprivacy`:
       - Email Address (linked, app functionality)
       - Name (linked, app functionality)
       - User ID (linked, app functionality)
       - User Content / Photos & Videos / Audio Data (linked, app
         functionality)
       - Product Interaction (linked, app functionality + analytics)
       - Device ID (linked, app functionality)
       - Crash Data (not linked, app functionality)
- [ ] ⚙️ Age Rating → 17+
       (UGC apps with unfiltered user content require 17+; any social
        with user-generated content gets +1 rating bump)
- [ ] ⚙️ Content Rights → declare you have rights for all content shown
       in screenshots / preview

## 7. App Store Listing

- [ ] ⚙️ Subtitle (≤ 30 chars): "Vertical video, your way"
- [ ] ⚙️ Promotional text (≤ 170 chars): updated weekly
- [ ] ⚙️ Description (≤ 4000 chars): see template in
       `app-store-listing-template.md` (write yourself)
- [ ] ⚙️ Keywords (≤ 100 chars total, comma-separated):
       e.g. `videos,creator,short video,social,reels,clips,maker,upload`
- [ ] ⚙️ Support URL: a public page with contact form / FAQ
- [ ] ⚙️ Marketing URL (optional): clipsmith.app
- [ ] ⚙️ Privacy Policy URL: `https://clipsmith.app/legal/privacy`
       (or wherever you host the static export)
- [ ] ⚙️ Terms of Use URL: `https://clipsmith.app/legal/terms`
       (Apple ToU is OK for paid services; we have our own ToS)

## 8. Screenshots

Required sizes (at least one set per device class):
- [ ] ⚙️ iPhone 6.7" (1290×2796 portrait) — iPhone 15 Pro Max simulator
- [ ] ⚙️ iPhone 6.5" (1242×2688) — iPhone 11 Pro Max
- [ ] ⚙️ iPhone 5.5" (1242×2208) — iPhone 8 Plus

Tip: open the simulator, navigate to feed/record/profile, ⌘S to save.
Avoid: status bar with personal info, screen recording artifacts, NSFW.

## 9. App Review Information

- [ ] ⚙️ Sign-in account: provide reviewer test account (username + password)
- [ ] ⚙️ Notes for reviewer: explain UGC moderation flow
       — point to report and block features
       — describe how violating content is removed within 24h
       — disclose royalty-free music library only (no third-party music)

## 10. TestFlight

- [ ] ⚙️ Add yourself + co-testers as Internal Testers
- [ ] ⚙️ Upload first build via Xcode → Product → Archive → Distribute
       → App Store Connect → Upload
- [ ] ⚙️ Wait for "Processing" to finish (~15 min)
- [ ] ⚙️ Run on physical device via TestFlight to verify push, camera

## 11. Submit for Review

- [ ] ⚙️ App Review → Submit for Review
- [ ] ⚙️ Expect 1–3 day initial review for a new app
- [ ] ⚙️ Plan for 1+ rejection round; common UGC rejection reasons:
       - 1.2 Moderation insufficient (we've shipped report + block)
       - 4.2.3 Minimum functionality / repackaged web (we have native
         camera, push, haptics — should be fine)
       - 5.1.1(v) Account deletion missing (we've shipped Settings →
         Delete my account)

## 12. Post-launch monitoring

- [ ] ⚙️ Watch Sentry for crash spikes
- [ ] ⚙️ Watch App Store Connect → Crashes
- [ ] ⚙️ Reply to App Store reviews within 24h

---

## Build commands

```bash
# Rebuild web bundle and sync into iOS app
cd frontend
npm run build && npx cap sync ios

# Open Xcode
open ios/App/App.xcodeproj

# Backend tests (run before tagging a release)
cd ..
source .venv-test/bin/activate
DATABASE_URL='sqlite:///test.db' JWT_SECRET_KEY='test' python -m pytest backend/tests
```
