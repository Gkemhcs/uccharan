"""Thin wrapper around the Gemini API for correction/tutoring calls.

Kept small and isolated on purpose: this is the one place that talks to
Gemini, so it's the one place tests mock out, and the one place we touch
if we ever add a fallback provider (e.g. Groq) or swap models.
"""

from typing import Literal

from google import genai
from google.genai import errors as genai_errors
from pydantic import BaseModel

from app.core.config import Settings
from app.core.errors import GeminiRateLimitedError, GeminiUnavailableError

CORRECTION_PROMPT_TEMPLATE = """You are a warm, encouraging English speaking tutor.
{address_instruction}
The student was asked to say this target sentence:
"{target_sentence}"
{focus_sound_instruction}
Speech recognition heard them say:
"{spoken_text}"

Compare the two. Respond in this exact format, nothing else:
CORRECT: yes or no
FEEDBACK: one short, encouraging sentence explaining any mistake in plain language \
(grammar, word choice, or likely mispronunciation implied by the transcript difference). \
If it's correct, give a short positive remark instead.
{native_explanation_instruction}
"""


class CorrectionResult(BaseModel):
    is_correct: bool
    feedback: str
    native_explanation: str | None = None


# --- Practice / roleplay conversation ("Practice with your Tutor") ---------

PRACTICE_PROMPT_TEMPLATE = """You are Teacher Uccharan, a warm, patient, encouraging spoken-English \
tutor helping an adult beginner-to-intermediate learner practice speaking English \
through a roleplay conversation built around what they just learned.

Today's lesson topic: {topic}
Your role: take on whatever everyday role naturally fits this topic (a shopkeeper, a \
neighbor, a doctor, a colleague, a friend — whatever the topic calls for) and start a \
realistic back-and-forth conversation that puts this topic's vocabulary and sentence \
patterns to use. This is NOT an open-ended "talk about anything" chat — stay focused on \
today's topic the way a real tutor assigns a speaking task right after teaching something.
{address_instruction}

This is a SPOKEN conversation — the learner hears your reply read aloud by \
text-to-speech, so:
- Keep your in-character reply SHORT: 1-2 simple sentences, using vocabulary and \
grammar a CEFR A1-B1 learner can follow.
- Stay fully in character for the scenario at all times.
- End your reply with a short follow-up question to keep the learner talking, \
unless it's a natural place for the conversation to wrap up.
- If the learner's message was empty, unclear, or looks like a speech-recognition \
error, warmly ask them to try saying it again — never criticize.
- Remember and naturally refer back to durable facts the learner has shared \
earlier in this conversation (their name, hometown, family, etc.) when it fits \
— a real tutor doesn't forget what a learner told them a few turns ago.
{summary_section}
Conversation so far:
{history_text}
Learner just said: "{learner_message}"

Respond in this exact format, nothing else:
REPLY: your short, in-character spoken reply
CORRECTION: if the learner's message had one clear English mistake worth mentioning, \
a short, encouraging correction (e.g. "Nice try! We usually say 'I went' instead of \
'I go' for something that already happened."). Only ever flag the single most \
important mistake, never a list. If there's no clear mistake worth flagging, write NONE.
{native_note_instruction}
"""


class PracticeMessage(BaseModel):
    speaker: Literal["learner", "tutor"]
    text: str


class PracticeTurnResult(BaseModel):
    tutor_reply: str
    correction: str | None = None
    native_note: str | None = None
    # Carried state for long-conversation memory — see continue_practice_conversation's
    # docstring. The client's only job is to forward these two values back
    # unchanged on the next turn; it never computes or inspects them itself.
    conversation_summary: str | None = None
    summarized_through_index: int = 0


# Only the most recent exchanges are sent to Gemini verbatim as context — keeps
# prompt size (and therefore latency/cost) bounded regardless of how long a
# practice session runs. Durable facts from OLDER turns aren't just dropped,
# though — see continue_practice_conversation.
_PRACTICE_HISTORY_WINDOW = 6

# Once this many messages have piled up since the last summarize pass,
# continue_practice_conversation folds the older ones into a fresh summary
# before generating its reply.
_SUMMARIZE_TRIGGER_SIZE = 14


# --- Listening comprehension ------------------------------------------------

LISTENING_PROMPT_TEMPLATE = """You are writing a short LISTENING comprehension exercise for an \
adult English learner (CEFR A1-B1), themed around: {topic}

Write a short passage — either a short realistic spoken exchange (2-3 lines, e.g. two people \
talking) or a short monologue (2-4 sentences) — the kind of thing the learner would actually \
need to understand out loud in real life for this topic. Simple, natural, everyday spoken \
English, nothing written-style or overly formal.

Then write ONE comprehension question about it. This question must test whether the learner \
UNDERSTOOD what was said — not a grammar or vocabulary quiz, and not something answerable \
without having listened (e.g. don't just ask to repeat a word verbatim). Give exactly 4 answer \
options, only one clearly correct, the other three plausible but wrong.

Respond in this exact format, nothing else:
PASSAGE: the short passage, as plain text a text-to-speech voice will read aloud
QUESTION: the comprehension question
OPTION_A: first option
OPTION_B: second option
OPTION_C: third option
OPTION_D: fourth option
CORRECT: the single letter of the correct option (A, B, C, or D)
EXPLANATION: one short, encouraging sentence explaining why that's the answer, referencing \
what was actually said in the passage
"""


class ListeningExercise(BaseModel):
    passage: str
    question: str
    options: list[str]
    correct_option_index: int
    explanation: str


SUMMARIZE_PROMPT_TEMPLATE = """You are keeping a short memory note for an English-speaking \
tutor bot, so it can remember facts a learner has shared earlier in a long practice \
conversation (their name, hometown, family, job, interests — anything worth \
referring back to later). This is bookkeeping, not something the learner sees.

{previous_summary_section}

New messages to fold in:
{history_text}

Respond in this exact format, nothing else:
SUMMARY: 2-3 short sentences capturing only the durable facts worth remembering \
(skip small talk and filler). Merge with anything already known above into one \
clean, updated note — don't just repeat the old note verbatim.
"""


class GeminiService:
    def __init__(self, settings: Settings):
        self._client = genai.Client(api_key=settings.google_api_key)
        self._model = settings.gemini_model

    def _generate(self, prompt: str):
        """
        The one place every prompt in this file actually reaches Gemini —
        translates the SDK's raw errors into GeminiRateLimitedError /
        GeminiUnavailableError (see app/core/errors.py) so callers, and the
        exception handlers registered in app/main.py, don't each need their
        own copy of this mapping.
        """
        try:
            return self._client.models.generate_content(model=self._model, contents=prompt)
        except genai_errors.ServerError as exc:
            raise GeminiUnavailableError(str(exc)) from exc
        except genai_errors.ClientError as exc:
            if exc.code == 429:
                raise GeminiRateLimitedError(str(exc)) from exc
            raise  # anything else (bad request, bad API key, ...) is our own bug — let it surface as a real 500

    def check_pronunciation_attempt(
        self,
        target_sentence: str,
        spoken_text: str,
        preferred_address_term: str | None = None,
        native_language: str | None = None,
        focus_sounds: list[str] | None = None,
    ) -> CorrectionResult:
        address_instruction = (
            f'Address the student warmly as "{preferred_address_term}" if it fits '
            f"naturally in your feedback — the way a caring family member would, not "
            f"formally."
            if preferred_address_term
            else ""
        )
        # This lesson's curriculum-authored target sound(s) — e.g. a lesson
        # teaching "th" words flags focus_sounds=["th"]. Telling Gemini about
        # it means feedback on a mispronunciation can name the actual sound
        # to work on ("the 'th' sound") instead of only describing the
        # transcript mismatch in the abstract.
        focus_sound_instruction = (
            f"This lesson is specifically teaching the {', '.join(focus_sounds)} "
            f"sound(s) — if the mismatch looks like a mispronunciation of one of "
            f"these, name the specific sound in your feedback so the student knows "
            f"exactly what to work on.\n"
            if focus_sounds
            else ""
        )
        native_explanation_instruction = (
            f"NATIVE_EXPLANATION: restate the FEEDBACK line in {native_language}, "
            f"simply and warmly, the way a patient native-{native_language}-speaking "
            f"tutor would explain it to a beginner. Do not just transliterate — "
            f"actually translate and explain."
            if native_language
            else ""
        )

        prompt = CORRECTION_PROMPT_TEMPLATE.format(
            target_sentence=target_sentence,
            spoken_text=spoken_text,
            address_instruction=address_instruction,
            focus_sound_instruction=focus_sound_instruction,
            native_explanation_instruction=native_explanation_instruction,
        )
        response = self._generate(prompt)
        return self._parse_response(response.text or "")

    def continue_practice_conversation(
        self,
        topic: str,
        history: list[PracticeMessage],
        learner_message: str,
        preferred_address_term: str | None = None,
        native_language: str | None = None,
        conversation_summary: str | None = None,
        summarized_through_index: int = 0,
    ) -> PracticeTurnResult:
        """Advances a roleplay conversation by one turn.

        `topic` is whatever the learner's current lesson is themed around
        (the Android client's current roadmap day, e.g. "Food & Ordering")
        — the tutor persona is built fresh from it every turn rather than
        looked up from a fixed scenario list, so practice always matches
        what was just taught, for any of the 90 days, with no separate
        scenario table to keep in sync. There is deliberately no
        "free conversation, no fixed topic" mode — see CURRICULUM.md §8.

        Owns the "when to compress older turns into a summary" decision
        entirely server-side: the client just forwards whatever `history`,
        `conversation_summary`, and `summarized_through_index` it was given
        back on the previous turn (or the defaults, on the first one) — it
        never decides when to summarize or calls a summarize endpoint
        itself. If enough un-summarized history has piled up, this makes one
        extra Gemini call to fold the older portion into an updated summary
        before generating the reply, and returns the (possibly updated)
        summary/index for the client to carry forward untouched next time.
        """
        updated_summary = conversation_summary
        updated_summarized_through_index = summarized_through_index

        unsummarized_count = len(history) - summarized_through_index
        summarize_cutoff = len(history) - _PRACTICE_HISTORY_WINDOW
        if unsummarized_count > _SUMMARIZE_TRIGGER_SIZE and summarize_cutoff > summarized_through_index:
            to_summarize = history[summarized_through_index:summarize_cutoff]
            updated_summary = self.summarize_conversation(to_summarize, conversation_summary)
            updated_summarized_through_index = summarize_cutoff

        address_instruction = (
            f'Address the student warmly as "{preferred_address_term}" if it fits '
            f"naturally — the way a caring family member would, not formally."
            if preferred_address_term
            else ""
        )
        native_note_instruction = (
            f"NATIVE_NOTE: if CORRECTION above is not NONE, restate it in "
            f"{native_language}, simply and warmly, the way a patient native-"
            f"{native_language}-speaking tutor would explain it to a beginner — "
            f"actually translate and explain, don't just transliterate. If "
            f"CORRECTION is NONE, write NONE."
            if native_language
            else ""
        )
        summary_section = (
            f"What you already know about the learner from earlier in this "
            f"conversation: {updated_summary}"
            if updated_summary
            else ""
        )
        recent_history = history[-_PRACTICE_HISTORY_WINDOW:]
        history_text = (
            "\n".join(f"{'Learner' if m.speaker == 'learner' else 'You'}: {m.text}" for m in recent_history)
            if recent_history
            else "(this is the first message)"
        )

        prompt = PRACTICE_PROMPT_TEMPLATE.format(
            topic=topic,
            address_instruction=address_instruction,
            summary_section=summary_section,
            history_text=history_text,
            learner_message=learner_message,
            native_note_instruction=native_note_instruction,
        )
        response = self._generate(prompt)
        result = self._parse_practice_response(response.text or "")
        return result.model_copy(
            update={
                "conversation_summary": updated_summary,
                "summarized_through_index": updated_summarized_through_index,
            }
        )

    def generate_listening_exercise(self, topic: str) -> ListeningExercise:
        """Generates one listening-comprehension round: a short passage the
        client's text-to-speech reads aloud (never shown as text until after
        answering — reading along would defeat the point) plus a multiple-choice
        comprehension question.

        Deliberately multiple-choice rather than "repeat what you heard":
        production-based checking (like check_pronunciation_attempt) grades
        against speech-recognition transcript matching, which is a weak proxy
        for whether the learner actually understood — they could stumble
        through a correct-sounding echo without following the meaning, or get
        marked wrong by a recognizer mishearing a correct answer. A
        comprehension question tests the actual skill this exercise is for.
        """
        prompt = LISTENING_PROMPT_TEMPLATE.format(topic=topic)
        response = self._generate(prompt)
        return self._parse_listening_response(response.text or "")

    @staticmethod
    def _parse_listening_response(raw_text: str) -> ListeningExercise:
        passage = ""
        question = ""
        options: dict[str, str] = {}
        correct_letter = "A"
        explanation = ""

        for line in raw_text.splitlines():
            line = line.strip()
            upper = line.upper()
            if upper.startswith("PASSAGE:"):
                passage = line.split(":", 1)[1].strip()
            elif upper.startswith("QUESTION:"):
                question = line.split(":", 1)[1].strip()
            elif upper.startswith("OPTION_A:"):
                options["A"] = line.split(":", 1)[1].strip()
            elif upper.startswith("OPTION_B:"):
                options["B"] = line.split(":", 1)[1].strip()
            elif upper.startswith("OPTION_C:"):
                options["C"] = line.split(":", 1)[1].strip()
            elif upper.startswith("OPTION_D:"):
                options["D"] = line.split(":", 1)[1].strip()
            elif upper.startswith("CORRECT:"):
                value = line.split(":", 1)[1].strip().upper()
                if value and value[0] in "ABCD":
                    correct_letter = value[0]
            elif upper.startswith("EXPLANATION:"):
                explanation = line.split(":", 1)[1].strip()

        # Index into `present_letters`/`ordered_options`, NOT into "ABCD" directly —
        # if a non-trailing letter is missing (e.g. only B and D came back), D's
        # position in "ABCD" (3) would point past the end of a 2-item options list.
        present_letters = [letter for letter in "ABCD" if letter in options]
        ordered_options = [options[letter] for letter in present_letters]
        correct_index = present_letters.index(correct_letter) if correct_letter in present_letters else 0

        return ListeningExercise(
            passage=passage or "Sorry, this exercise couldn't be generated — please try again.",
            question=question or "What did you hear?",
            options=ordered_options,
            correct_option_index=correct_index,
            explanation=explanation,
        )

    def summarize_conversation(
        self,
        history: list[PracticeMessage],
        previous_summary: str | None = None,
    ) -> str:
        """Compresses older practice-conversation turns into a short, durable-facts note.

        Called by the client periodically as a conversation grows past what
        fits in `_PRACTICE_HISTORY_WINDOW`, so facts don't silently vanish
        from the tutor's context once their raw turn ages out of the window.
        """
        previous_summary_section = (
            f"What you already knew before these new messages: {previous_summary}"
            if previous_summary
            else "(nothing known yet — this is the first summary)"
        )
        history_text = (
            "\n".join(f"{'Learner' if m.speaker == 'learner' else 'You'}: {m.text}" for m in history)
            if history
            else "(no new messages)"
        )

        prompt = SUMMARIZE_PROMPT_TEMPLATE.format(
            previous_summary_section=previous_summary_section,
            history_text=history_text,
        )
        response = self._generate(prompt)
        return self._parse_summary_response(response.text or "", fallback=previous_summary or "")

    @staticmethod
    def _parse_summary_response(raw_text: str, fallback: str) -> str:
        for line in raw_text.splitlines():
            line = line.strip()
            if line.upper().startswith("SUMMARY:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    return value
        return fallback

    @staticmethod
    def _parse_practice_response(raw_text: str) -> PracticeTurnResult:
        reply = "Sorry, could you say that again?"
        correction: str | None = None
        native_note: str | None = None

        for line in raw_text.splitlines():
            line = line.strip()
            if line.upper().startswith("REPLY:"):
                reply = line.split(":", 1)[1].strip() or reply
            elif line.upper().startswith("CORRECTION:"):
                value = line.split(":", 1)[1].strip()
                correction = None if not value or value.upper() == "NONE" else value
            elif line.upper().startswith("NATIVE_NOTE:"):
                value = line.split(":", 1)[1].strip()
                native_note = None if not value or value.upper() == "NONE" else value

        return PracticeTurnResult(tutor_reply=reply, correction=correction, native_note=native_note)

    @staticmethod
    def _parse_response(raw_text: str) -> CorrectionResult:
        is_correct = False
        feedback = "Sorry, I couldn't evaluate that attempt — please try again."
        native_explanation: str | None = None

        for line in raw_text.splitlines():
            line = line.strip()
            if line.upper().startswith("CORRECT:"):
                is_correct = line.split(":", 1)[1].strip().lower().startswith("y")
            elif line.upper().startswith("FEEDBACK:"):
                feedback = line.split(":", 1)[1].strip()
            elif line.upper().startswith("NATIVE_EXPLANATION:"):
                native_explanation = line.split(":", 1)[1].strip()

        return CorrectionResult(is_correct=is_correct, feedback=feedback, native_explanation=native_explanation)
