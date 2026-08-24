"""Thin wrapper around the Gemini API for correction/tutoring calls.

Kept small and isolated on purpose: this is the one place that talks to
Gemini, so it's the one place tests mock out, and the one place we touch
if we ever add a fallback provider (e.g. Groq) or swap models.
"""

from typing import Literal

from google import genai
from pydantic import BaseModel

from app.core.config import Settings

CORRECTION_PROMPT_TEMPLATE = """You are a warm, encouraging English speaking tutor.
{address_instruction}
The student was asked to say this target sentence:
"{target_sentence}"

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

    def check_pronunciation_attempt(
        self,
        target_sentence: str,
        spoken_text: str,
        preferred_address_term: str | None = None,
        native_language: str | None = None,
    ) -> CorrectionResult:
        address_instruction = (
            f'Address the student warmly as "{preferred_address_term}" if it fits '
            f"naturally in your feedback — the way a caring family member would, not "
            f"formally."
            if preferred_address_term
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
            native_explanation_instruction=native_explanation_instruction,
        )
        response = self._client.models.generate_content(model=self._model, contents=prompt)
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
        response = self._client.models.generate_content(model=self._model, contents=prompt)
        result = self._parse_practice_response(response.text or "")
        return result.model_copy(
            update={
                "conversation_summary": updated_summary,
                "summarized_through_index": updated_summarized_through_index,
            }
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
        response = self._client.models.generate_content(model=self._model, contents=prompt)
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
