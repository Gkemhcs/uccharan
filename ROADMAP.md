# Uccharan — Build Roadmap

Locked-in stack: Kotlin + Jetpack Compose (Material 3) · FastAPI on Render ·
Gemini API via Google AI Studio · on-device Android SpeechRecognizer + TextToSpeech ·
Firebase Auth + Firestore · target: Play Store release.

Tracking status here so every session picks up exactly where the last one left off.

---

## Phase 0 — Setup

- [x] Android Studio project created (Compose, Empty Activity)
- [x] Package fixed to `com.uccharan.app`
- [x] FastAPI backend scaffolded: `/health`, `/api/v1/correct` (Gemini-backed), tests passing
- [x] Root Git repo initialized, first commit made
- [ ] Push repo to GitHub
- [ ] Create Firebase project → enable Authentication + Firestore (Spark/free plan)
- [ ] Add Android app to Firebase project → drop `google-services.json` into `android/app/`
- [ ] Create Render account, connect GitHub (service creation happens when backend is deploy-ready)

## Phase 1 — MVP core loop (one lesson track, ~10-15 lessons)

- [ ] App theming: Material 3 color scheme/typography for Uccharan (not the default purple template)
- [ ] Navigation graph: Home/Roadmap → Lesson screen → Result/Feedback screen
- [ ] Lesson content model: simple JSON/local data class list of target sentences (no CMS yet)
- [ ] Firebase Auth: anonymous or email sign-in (minimum viable — don't over-build this yet)
- [ ] Mic recording screen: request `RECORD_AUDIO` permission, use `SpeechRecognizer` to capture attempt
- [ ] Wire recorded transcript → backend `/api/v1/correct` → show feedback (correct/incorrect + explanation)
- [ ] On-device `TextToSpeech` reads the target sentence (and corrected version) aloud
- [ ] Progress write to Firestore on lesson completion
- [ ] Unit tests: ViewModels, repository layer
- [ ] Compose UI tests: the core record → feedback → complete flow
- [ ] **Milestone: one full lesson playable end-to-end on a real device, no crashes**

## Phase 2 — Roadmap & structure

- [ ] Multiple tracks/levels
- [ ] Visual roadmap/path screen showing progress
- [ ] Lesson unlocking logic, streaks

## Phase 3 — AI depth & polish

- [ ] Free-form conversation practice mode
- [ ] Translation-on-tap for unfamiliar words
- [ ] Word-level error highlighting in feedback UI
- [ ] (Optional upgrade) Cloud Text-to-Speech Neural2 voices, once GCP billing is sorted calmly

## Phase 4 — Production hardening for Play Store

- [ ] Privacy Policy page (mic audio + speech data sent to Gemini — must disclose)
- [ ] Play Console Data Safety form
- [ ] Release signing (upload key), R8/ProGuard rules
- [ ] Closed testing track before public release
- [ ] Firebase Crashlytics wired in, basic Render uptime check
- [ ] Render upgraded off free tier (removes cold-start sleep) before real users land

---

**Current focus: finishing Phase 0.** Next concrete step: push to GitHub.
