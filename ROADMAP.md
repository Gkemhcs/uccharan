# Uccharan — Build Roadmap

Locked-in stack: Kotlin + Jetpack Compose (Material 3) · FastAPI on Render ·
Gemini API via Google AI Studio · on-device Android SpeechRecognizer + TextToSpeech ·
Firebase Auth + Firestore · target: Play Store release.

Content structure, curriculum framework, and the full feature vision live in
[`CURRICULUM.md`](./CURRICULUM.md) — read it before building Phase 1's lesson
content model or Phase 2/3 features. This file says *when*; that one says *what*.

Tracking status here so every session picks up exactly where the last one left off.

---

## Phase 0 — Setup

- [x] Android Studio project created (Compose, Empty Activity)
- [x] Package fixed to `com.uccharan.app`
- [x] FastAPI backend scaffolded: `/health`, `/api/v1/correct` (Gemini-backed), tests passing
- [x] Root Git repo initialized, first commit made
- [x] Push repo to GitHub (https://github.com/Gkemhcs/uccharan)
- [x] Create Firebase project → enable Authentication (Email/Password + Google) + Firestore (Spark/free plan)
- [x] Add Android app to Firebase project → `google-services.json` placed in `android/app/`, debug SHA-1/SHA-256 registered
- [x] Google Services Gradle plugin + Firebase Auth/Firestore + Credential Manager (Google Sign-In) dependencies wired in; `./gradlew assembleDebug` succeeds
- [x] Create Render account (Google auth sign-in) — service creation still pending until backend is deploy-ready

## Phase 1 — MVP core loop (one lesson track, ~10-15 lessons)

- [ ] App theming: Material 3 color scheme/typography for Uccharan (not the default purple template)
- [ ] Navigation graph: Home/Roadmap → Lesson screen → Result/Feedback screen
- [ ] Lesson content model: `speak_repeat` type only, but full schema from `CURRICULUM.md` §2 — seed ~10-15 Foundations-track lessons directly into Firestore (no CMS/authoring UI yet, just seeded documents)
- [x] Backend: native language personalization — `/api/v1/correct` accepts `preferred_address_term` + `native_language`, returns bilingual `native_explanation`; verified live with Telugu (see `CURRICULUM.md` §6.5)
- [ ] Firebase Auth: Email/Password + Google Sign-In (deps already wired — build the actual sign-in screen)
- [ ] Onboarding: ask native language + preferred address term (suggest Telugu Nanna/Amma pattern when Telugu selected), store in Firestore user profile
- [ ] Mic recording screen: request `RECORD_AUDIO` permission, use `SpeechRecognizer` to capture attempt
- [ ] Wire recorded transcript → backend `/api/v1/correct` (pass stored native language/address prefs) → show feedback (correct/incorrect + English explanation + native-language explanation when set)
- [ ] On-device `TextToSpeech` reads the target sentence (and corrected version) aloud
- [ ] Log every attempt (target, transcript, correct/not, timestamp) to Firestore — feeds Phase 3 weak-point analytics for free later
- [ ] Progress write to Firestore on lesson completion
- [ ] Unit tests: ViewModels, repository layer
- [ ] Compose UI tests: the core record → feedback → complete flow
- [ ] **Milestone: one full lesson playable end-to-end on a real device, no crashes**

## Phase 2 — Roadmap & structure

- [ ] Placement test (adaptive, drops learner into the right track/unit)
- [ ] Multiple tracks/levels (Foundations / Everyday Fluency / Professional & Exam Mastery — see `CURRICULUM.md` §1)
- [ ] Visual roadmap/path screen showing progress
- [ ] Lesson unlocking logic, streaks + streak-freeze
- [ ] SRS vocabulary review tab (Leitner-style, see `CURRICULUM.md` §3)
- [ ] Minimal-pair pronunciation drills (`minimal_pair` lesson type)

## Phase 3 — AI depth & polish

- [ ] Roleplay/conversation mode with seeded scenarios (see `CURRICULUM.md` §5)
- [ ] Slow-motion shadowing mode
- [ ] Translation-on-tap for unfamiliar words
- [ ] Listening dictation exercises
- [ ] Word-level error highlighting in feedback UI
- [ ] Weak-point analytics screen (derived from logged attempt history)
- [ ] **Decision point**: evaluate adding Azure Pronunciation Assessment for real phoneme-level scoring (see `CURRICULUM.md` §4 for the honest gap vs current approach) — only if pronunciation becomes the differentiator worth the added cost/complexity
- [ ] (Optional upgrade) Cloud Text-to-Speech Neural2 voices, once GCP billing is sorted calmly

## Phase 3.5 — Differentiators (prioritize by real user feedback, don't pre-build)

- [ ] Voice journal (daily recording, track progress over time)
- [ ] IELTS/TOEFL speaking-section simulator
- [ ] Idioms & slang micro-lessons
- [ ] Adaptive difficulty from error-rate trend
- [ ] Home-screen widget: word/phrase of the day
- [ ] Accent target selection (US/UK/Australian)

## Phase 4 — Production hardening for Play Store

- [ ] Privacy Policy page (mic audio + speech data sent to Gemini — must disclose)
- [ ] Play Console Data Safety form
- [ ] Release signing (upload key), R8/ProGuard rules
- [ ] Add release keystore's SHA-1/SHA-256 to Firebase (Google Sign-In breaks in release builds otherwise — debug fingerprints were added in Phase 0)
- [ ] Closed testing track before public release
- [ ] Firebase Crashlytics wired in, basic Render uptime check
- [ ] Render upgraded off free tier (removes cold-start sleep) before real users land

---

**Phase 0 complete.** Current focus: Phase 1 — starting with the lesson content
model (schema-driven, seeded into Firestore per `CURRICULUM.md` §2) and the
sign-in screen, then the mic → correct → feedback loop.

**Dev environment note:** if `./gradlew` fails on this machine with `SSLHandshakeException` /
"PKIX path building failed" while resolving plugins, that's this network/JVM's trust
store, not the project. Fix lives in `~/.gradle/gradle.properties` (machine-local,
not committed) — points the JVM at a merged trust store
(`~/.gradle/uccharan-truststore/merged-cacerts`, built from the JBR's default CAs +
macOS's trusted roots) with `-Dcom.sun.security.enableAIAcaIssuers=true` for hosts
(like dl.google.com) that send an incomplete certificate chain.
