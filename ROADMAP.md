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

- [x] App theming: real Material 3 identity — teal/amber brand colors, Newsreader (serif, headlines/lesson sentences) + Plus Jakarta Sans (UI) bundled as static fonts, gradient buttons/icons, layered shadows. Design canvas: see the "Uccharan Design System" artifact (published this session) for the reference mockups; implementation matches it closely, verified on-device
- [x] Navigation graph: SignIn/PhoneSignIn → Onboarding → Home/Roadmap → Lesson screen (idle/listening/feedback states) → Profile → Quiz
- [x] Lesson content model: `speak_repeat` type, full schema from `CURRICULUM.md` §2 plus bilingual `nativeTranslation`/`nativeMeaning` fields — 40 lessons across Week 1 (Days 1-7) seeded into Firestore via `backend/scripts/seed_week1_content.py` (test-mode REST rules; real service-account-based seeding still a later hardening item, see Phase 4)
- [x] Backend: native language personalization — `/api/v1/correct` accepts `preferred_address_term` + `native_language`, returns bilingual `native_explanation`; verified live with Telugu (see `CURRICULUM.md` §6.5)
- [x] Firebase Auth: Email/Password + Google Sign-In + Phone (OTP) — all three wired and UI built, with friendly validation (password policy checklist, plain-language Firebase error mapping) instead of raw SDK error text
- [x] Onboarding: native language + preferred address term (Telugu Nanna/Amma suggestion), stored in Firestore user profile — verified on-device; same preference editor now also lives in Profile → Settings
- [x] Mic recording screen: `RECORD_AUDIO` permission flow + `SpeechRecognizer` — verified on-device (idle + listening states); live end-to-end mic audio test still pending, deferred to the user's own final pass
- [x] Wire recorded transcript → backend `/api/v1/correct` → feedback card (English + native-language explanation, Telugu TTS playback on the native explanation) — verified live end-to-end with real Gemini responses
- [x] On-device `TextToSpeech` reads the target sentence aloud (English) and the native explanation aloud (Telugu, `Locale("te","IN")`)
- [x] Log every attempt (target, transcript, correct/not, timestamp) to Firestore — `LessonRepository.logAttempt` is called from `LessonViewModel.logAttemptAndMaybeComplete` on every attempt; feeds Phase 3 weak-point analytics for free later
- [x] Progress write to Firestore on lesson completion (`markLessonComplete` + `addXp`), plus real sequential lesson-unlock logic (a lesson stays locked until the previous one is completed) — matches the design's locked/active/completed states
- [x] "Skip this section" — bulk-completes every remaining lesson in the learner's current day (no XP, since nothing was demonstrated), with a confirmation dialog; generalizes to whichever day the learner is on, not just Day 1
- [x] Profile & Settings screen: avatar/name/email, total XP, per-week roadmap progress (Complete/In progress/Coming soon, computed from passed quiz ids), quiz score history, editable native-language/address-term preferences, log out
- [x] 30-day roadmap structure (`data/roadmap/RoadmapPlan.kt`) with real, researched content for Week 1 (Days 1-7) — see `CURRICULUM.md` §8 for the research grounding and citations; Days 8-30 are planned themes only, seeded later the same way
- [x] Quiz feature: 5-question multiple-choice quiz per day (`quizzes` Firestore collection), scored client-side (no backend/AI call needed), 70% to pass, awards XP and advances the learner to the next day on a pass — bilingual (Telugu) answer explanations
- [x] Home screen redesigned as a Duolingo/ELSA-style winding path (`RoadmapPath`/`PathNode` in `HomeScreen.kt`) — lesson/quiz nodes on a dashed snake path, locked/active/completed states, pulsing "START"/"QUIZ" bubble on the current node — rather than a flat checklist
- [x] Achievement micro-animations: quiz pass gets a spring bounce-in badge + a small confetti burst, a fail gets a gentle shake; the lesson feedback card entrance-animates (scale+fade, with a shake on an incorrect attempt) — same "own it or admit it" spirit applied to feeling, not just function
- [x] Stale-Home-data bug fixed: `HomeViewModel.loadLessons()` re-fires on `ON_RESUME` (lifecycle observer), so returning from a finished Lesson/Quiz shows fresh lock/completion state instead of stale data from before navigating away
- [x] Unit tests: ViewModels, repository-adjacent logic — 38 passing (auth incl. validation, onboarding, home incl. unlock/skip/quiz-ready logic, lesson, phone sign-in, correction API client, quiz scoring/pass-threshold, profile progress computation)
- [ ] Compose UI tests: the core record → feedback → complete flow (not started — manual on-device verification done instead so far)
- [ ] **Milestone: one full lesson playable end-to-end on a real device, no crashes** — verified through listening state; full correct/incorrect feedback round-trip verified separately via curl against the live backend, not yet via real mic audio on-device (emulator has no real audio input) — user has said they'll do this final pass themselves
    
## Phase 2 — Roadmap & structure

- [ ] Placement test (adaptive, drops learner into the right track/unit)
- [ ] Multiple CEFR tracks/levels (Foundations / Everyday Fluency / Professional & Exam Mastery — see `CURRICULUM.md` §1); the 30-day parent track shipped in Phase 1 is a separate, complementary thing — a fixed daily sequence, not a level-select
- [x] Visual roadmap/path screen showing progress — shipped early, in Phase 1: Home's winding lesson/quiz path + Profile's per-week progress view
- [x] Lesson unlocking logic — shipped in Phase 1 (sequential within a day; day-to-day unlock via quiz pass)
- [ ] Streaks + streak-freeze
- [ ] SRS vocabulary review tab (Leitner-style, see `CURRICULUM.md` §3) — `VocabWord`/`nativeMeaning` schema is already SRS-ready, review UI itself not built
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

**Phase 0 complete. Phase 1 core loop — plus a good chunk of Phase 2 —
built, styled, seeded with real content, and verified on-device.**
Remaining before the Phase 1 milestone is fully closed: Compose UI tests,
a real (non-test-mode) Firestore seeding path for lessons/quizzes, and a
real-device mic test with actual audio (only tested via emulator + curl so
far — the user has said they'll run this final pass themselves). Content-wise,
Week 1 (Days 1-7) of the 30-day roadmap is fully authored and seeded;
Days 8-30 are planned themes only (`RoadmapPlan.kt`), to be authored and
seeded the same way as a follow-up rather than filled in shallowly now.

**Dev environment note:** if `./gradlew` fails on this machine with `SSLHandshakeException` /
"PKIX path building failed" while resolving plugins, that's this network/JVM's trust
store, not the project. Fix lives in `~/.gradle/gradle.properties` (machine-local,
not committed) — points the JVM at a merged trust store
(`~/.gradle/uccharan-truststore/merged-cacerts`, built from the JBR's default CAs +
macOS's trusted roots) with `-Dcom.sun.security.enableAIAcaIssuers=true` for hosts
(like dl.google.com) that send an incomplete certificate chain.
