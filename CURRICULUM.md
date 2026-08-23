# Uccharan — Curriculum & Feature Vision

This is the "what would it actually take for someone to go from zero to fluent
using only this app" document. `ROADMAP.md` says *when* we build things; this
says *what* we build. Read alongside it.

Grounded against what production apps actually do well (Aug 2026): ELSA Speak
(deepest phoneme-level pronunciation scoring), Speak (most natural open-ended
roleplay conversation), Duolingo (best structured, gamified progression).
Uccharan's shape: Duolingo's structure + Speak's roleplay depth + as close to
ELSA's pronunciation rigor as a Google-only stack gets us (honest gap noted
below, with an upgrade path).

---

## 1. The mastery framework

Content is organized around **CEFR levels** (the same A1–C2 scale every
serious language program uses — learners and any future resume/certificate
claim will recognize it) crossed with **6 skill pillars**:

| Pillar | What it trains |
|---|---|
| Pronunciation | Individual sounds, word stress, sentence rhythm/intonation |
| Vocabulary | Active recall, not just recognition — via spaced repetition |
| Grammar | Pattern usage in context, not rule memorization |
| Listening | Comprehension at natural native speed |
| Speaking / Fluency | Producing sentences under time pressure, without translating in your head |
| Real-world competence | Using English in actual situations — ordering food, interviews, small talk |

### Tracks (maps to Phase 2's "multiple tracks")

1. **Foundations** (A1–A2) — survival English: greetings, numbers, daily
   routines, simple questions. Heavy pronunciation drilling — this is where
   accent habits get set, so it deserves the most repetition.
2. **Everyday Fluency** (B1–B2) — the biggest track. Opinions, storytelling,
   phone calls, small talk, disagreeing politely. This is where roleplay
   conversation mode carries most of the weight.
3. **Professional & Exam Mastery** (C1–C2) — workplace English, presentations,
   negotiation, and dedicated **IELTS/TOEFL speaking-section simulators**
   (timed prompts, examiner-style follow-ups) — a well-known reason people
   pay for ELSA/Speak.

A **placement test** (10-15 adaptive speaking/listening items) on first
launch drops a learner into the right track/unit instead of forcing everyone
through A1. This should land in Phase 2, not Phase 1 — MVP can default
everyone to Foundations Unit 1.

---

## 2. Lesson content — the actual schema

Upgrading Phase 1's "simple JSON list of target sentences" to something that
can carry the full framework above without a rewrite later. One exercise
type isn't enough for real mastery — mixing these within a unit is what
makes practice actually work (this is standard spaced-practice pedagogy, not
just variety for its own sake):

```json
{
  "id": "found-a1-greetings-03",
  "track": "foundations",
  "cefr_level": "A1",
  "unit": "Greetings & Introductions",
  "type": "speak_repeat",
  "skill_focus": ["pronunciation", "speaking"],
  "prompt": {
    "target_sentence": "Nice to meet you.",
    "focus_sounds": ["/iː/ in 'meet'", "linking 'nice to' -> 'nice-tuh'"],
    "vocab_introduced": [{ "word": "nice", "meaning": "pleasant, kind" }],
    "grammar_note": "Fixed phrase — doesn't literally translate word-for-word in most languages, so don't overthink the grammar here."
  },
  "success_criteria": { "min_transcript_similarity": 0.85 },
  "xp_reward": 10
}
```

Other `type` values the engine needs to support (not all in MVP, but the
schema should allow them from day one so content authored now doesn't need
migration):

- `speak_repeat` — MVP's core loop (say the target sentence, get corrected)
- `minimal_pair` — "ship" vs "sheep" style drills; the single highest-leverage
  pronunciation exercise type and cheap to generate with Gemini
- `listening_dictation` — hear a sentence (TTS), type/say it back
- `vocab_recall` — SRS-driven, not part of a fixed lesson (see §3)
- `roleplay` — multi-turn scenario with an AI persona (§4)
- `free_response` — open question, graded on content + grammar, not exact match

### Where content lives
Store lessons in **Firestore**, not bundled JSON in the app. Reasoning: with
JSON-in-APK, adding or fixing a single lesson means a Play Store release
(days of review lag); with Firestore, it's an instant content update. This
is a correct-from-day-one decision, not scope creep — swapping later means
migrating every lesson reference. Cache fetched units locally (Room or
DataStore) so lessons already downloaded work offline.

---

## 3. Vocabulary retention — spaced repetition (SRS)

The thing most "lesson-based" apps get wrong: you see a word once and never
again. Real retention needs spaced repetition (Leitner-box style is simplest
to implement correctly):

- Every `vocab_introduced` word from a completed lesson enters the learner's
  personal SRS deck (a Firestore subcollection per user)
- Review interval grows on correct recall (1 day → 3 → 7 → 21 → …), resets on
  failure
- A daily "Review" tab surfaces due words — mixing production (say it) and
  recognition (pick the meaning)
- This is Phase 2 work, but the Firestore data model for it should be
  sketched before Phase 1 ships so `vocab_introduced` isn't a throwaway field

---

## 4. Speech & pronunciation — what's actually achievable, honestly

Current architecture (on-device STT transcript compared against target +
Gemini explains mismatches) gets you real value: catches wrong words, wrong
grammar, and — indirectly — bad pronunciation (if speech recognition
mis-hears "ship" as "sheep," that's a pronunciation signal even without
phoneme scoring).

**What it can't do, and what real ELSA-style scoring requires:** exact
phoneme-level accuracy (e.g. "your /θ/ in 'think' was 62% accurate")
needs a dedicated pronunciation-assessment model (Azure Speech is the
industry option here — we deliberately excluded it earlier for the
Google-only/no-extra-billing constraint). Worth being upfront about that
ceiling rather than overselling on-device STT as something it isn't.

**What we can do within the Google-only constraint to close the gap
significantly:**
- **Confidence-score signal**: Android's `SpeechRecognizer` returns
  per-result confidence scores — low confidence on a specific word is a
  usable (if coarse) mispronunciation signal, free, already available
- **Minimal-pair drills** (`ship`/`sheep`, `bit`/`beat`) — doesn't need
  phoneme scoring at all, just "did the recognizer transcribe the RIGHT
  word out of a known confusable pair" — cheap, effective, high value
- **Slow-motion shadowing**: TTS plays a sentence at 0.7x speed, learner
  mimics, on-device STT checks the attempt — no scoring needed, pure
  practice mode
- **Upgrade path, not a blocker**: if pronunciation becomes the app's
  differentiator later, Azure Pronunciation Assessment can be added as one
  more backend service call without touching the Android app at all (backend
  already abstracts "correction" behind one endpoint) — flagging this in
  Phase 3 as an explicit decision point, not deciding it now

---

## 5. Roleplay / conversation mode (the "Speak app" feature)

Multi-turn, in-character conversation with an AI persona is what makes an
app feel alive rather than like a flashcard deck. Concretely: Gemini holds a
system prompt defining a scenario + persona ("You are a barista at a busy
NYC coffee shop"), the learner speaks their turn, Gemini responds in
character AND separately flags any errors after the exchange (not
interrupting mid-conversation — that kills the natural feel).

Scenario examples to seed at launch: ordering food, job interview, small
talk with a coworker, asking for directions, a phone call rescheduling an
appointment, a doctor's visit. This is Phase 3 work but is the single
highest-value differentiator once the core loop (Phase 1) is solid — it's
what turns "drilling sentences" into "practicing for real life."

---

## 6. Feature list — grouped, mapped onto existing roadmap phases

Nothing here changes Phase 1's tight scope — it stays the mic → correct →
feedback loop. This just makes sure Phase 1's data model doesn't box out
everything below.

**Phase 2 additions** (builds on Phase 1's roadmap/structure work):
- Placement test
- SRS vocabulary review tab
- Minimal-pair pronunciation drills
- Streaks + daily goal + streak-freeze (standard, proven retention mechanic)

**Phase 3 additions** (builds on Phase 1's AI-depth work):
- Roleplay/conversation mode with seeded scenarios
- Slow-motion shadowing mode
- Translation-on-tap (already planned)
- Listening dictation exercises
- Weak-point analytics ("you struggle most with past tense" — derived from
  logged correction history, genuinely easy to compute since we already
  store every attempt)

**New — Phase 3.5, "differentiators"** (post-core-loop polish, prioritize by
what users actually ask for once Phase 1-3 are live, don't pre-build):
- Voice journal — daily 60-second free recording, saved over time, so a
  learner can literally hear their own progress after a month (strong
  emotional hook, cheap to build: just store audio + transcript + date)
- IELTS/TOEFL speaking-section simulator (timed prompts, examiner-style
  follow-up questions) — clear monetization angle if that's ever a goal
  later, exam-prep is what people pay for
  ([ELSA charges ~$12/mo largely on this](https://www.upskillist.com/blog/best-ai-language-learning-apps/))
- Idioms & slang micro-lessons (short, high-engagement, shareable content)
- Adaptive difficulty — auto-adjust lesson difficulty from error-rate trend,
  not just fixed unit progression
- Home-screen widget: word/phrase of the day
- Optional accent target selection (US/UK/Australian) — changes which TTS
  voice and which "correct" pronunciation target is used

Explicitly **not** planned unless requested: social features / leaderboards.
They drive engagement in gamified apps but add real backend complexity
(friend graphs, moderation) for a learner-outcome-focused app — worth
revisiting only if retention data later shows it's needed, not building on
spec now.

---

## 7. What this changes in Phase 1, concretely

- Lesson content model: build against the schema in §2 from the start
  (even though only `speak_repeat` ships in Phase 1)
- Lessons live in Firestore, not bundled JSON — small extra setup now, saves
  a painful migration later
- Every correction attempt gets logged (attempt text, target, correct/not,
  timestamp) — costs nothing extra now, is the entire data source for
  weak-point analytics in Phase 3
