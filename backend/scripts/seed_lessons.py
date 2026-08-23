"""One-off script to seed Foundations-track lessons into Firestore.

Uses the Firestore REST API directly (no service account needed) — this
relies on Firestore's default "test mode" security rules being open, which
they are for the first 30 days of a new project. Once real security rules
are in place, this script needs a service account instead (see
CURRICULUM.md §2 for why lessons live in Firestore rather than bundled JSON).

Usage:
    python3 backend/scripts/seed_lessons.py
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

PROJECT_ID = "uccharan-87bcf"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/lessons"

# Matches the Lesson/LessonPrompt/VocabWord schema in
# android/app/.../data/model/Lesson.kt and CURRICULUM.md §2.
LESSONS = [
    {
        "id": "found-a1-greet-01",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 1,
        "targetSentence": "Hello, how are you?",
        "focusSounds": ["/h/ in 'hello'"],
        "vocab": [{"word": "hello", "meaning": "a greeting"}],
        "grammarNote": "A fixed greeting phrase — used the same way every time.",
    },
    {
        "id": "found-a1-greet-02",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 2,
        "targetSentence": "I am fine, thank you.",
        "focusSounds": ["/θ/ in 'thank'"],
        "vocab": [{"word": "fine", "meaning": "okay, well"}],
        "grammarNote": "'I am' is often the response to 'how are you?'",
    },
    {
        "id": "found-a1-greet-03",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 3,
        "targetSentence": "Nice to meet you.",
        "focusSounds": ["/iː/ in 'meet'", "linking 'nice to' -> 'nice-tuh'"],
        "vocab": [{"word": "nice", "meaning": "pleasant, kind"}],
        "grammarNote": "A fixed phrase said when meeting someone for the first time.",
    },
    {
        "id": "found-a1-greet-04",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 4,
        "targetSentence": "My name is Alex.",
        "focusSounds": ["/æ/ in 'Alex'"],
        "vocab": [{"word": "name", "meaning": "what you are called"}],
        "grammarNote": "'My name is ___' — the standard way to introduce yourself.",
    },
    {
        "id": "found-a1-greet-05",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 5,
        "targetSentence": "Where are you from?",
        "focusSounds": ["/w/ in 'where'"],
        "vocab": [{"word": "from", "meaning": "indicates origin"}],
        "grammarNote": "A common question when meeting someone new.",
    },
    {
        "id": "found-a1-greet-06",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 6,
        "targetSentence": "I am from India.",
        "focusSounds": ["/ɪ/ in 'India'"],
        "vocab": [{"word": "India", "meaning": "a country"}],
        "grammarNote": "'I am from ___' states your country of origin.",
    },
    {
        "id": "found-a1-greet-07",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 7,
        "targetSentence": "See you later.",
        "focusSounds": ["/l/ in 'later'"],
        "vocab": [{"word": "later", "meaning": "at a future time"}],
        "grammarNote": "A casual way to say goodbye.",
    },
    {
        "id": "found-a1-greet-08",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 8,
        "targetSentence": "Have a good day.",
        "focusSounds": ["/g/ in 'good'"],
        "vocab": [{"word": "good", "meaning": "pleasant, nice"}],
        "grammarNote": "A polite phrase used when parting.",
    },
    {
        "id": "found-a1-greet-09",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 9,
        "targetSentence": "What is your name?",
        "focusSounds": ["/w/ in 'what'"],
        "vocab": [{"word": "your", "meaning": "belonging to you"}],
        "grammarNote": "A direct question to learn someone's name.",
    },
    {
        "id": "found-a1-greet-10",
        "track": "foundations",
        "cefrLevel": "A1",
        "unit": "Greetings & Introductions",
        "order": 10,
        "targetSentence": "It was nice talking to you.",
        "focusSounds": ["/t/ in 'talking'"],
        "vocab": [{"word": "talking", "meaning": "speaking with someone"}],
        "grammarNote": "Past tense — said at the end of a conversation.",
    },
]


def to_firestore_value(value):
    if isinstance(value, bool):
        return {"booleanValue": value}
    if isinstance(value, int):
        return {"integerValue": str(value)}
    if isinstance(value, str):
        return {"stringValue": value}
    if isinstance(value, list):
        return {"arrayValue": {"values": [to_firestore_value(v) for v in value]}}
    if isinstance(value, dict):
        return {"mapValue": {"fields": {k: to_firestore_value(v) for k, v in value.items()}}}
    raise TypeError(f"Unsupported type for Firestore value: {type(value)}")


def build_document(lesson: dict) -> dict:
    fields = {
        "id": lesson["id"],
        "track": lesson["track"],
        "cefrLevel": lesson["cefrLevel"],
        "unit": lesson["unit"],
        "type": "speak_repeat",
        "order": lesson["order"],
        "xpReward": 10,
        "prompt": {
            "targetSentence": lesson["targetSentence"],
            "focusSounds": lesson["focusSounds"],
            "vocabIntroduced": lesson["vocab"],
            "grammarNote": lesson["grammarNote"],
        },
    }
    return {"fields": {k: to_firestore_value(v) for k, v in fields.items()}}


def seed():
    for lesson in LESSONS:
        document = build_document(lesson)
        url = f"{BASE_URL}?documentId={lesson['id']}"
        request = urllib.request.Request(
            url,
            data=json.dumps(document).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request) as response:
                response.read()
            print(f"seeded {lesson['id']}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            if e.code == 409 or "already exists" in body:
                print(f"skipped {lesson['id']} (already exists)")
            else:
                print(f"FAILED {lesson['id']}: {e.code} {body}")


if __name__ == "__main__":
    seed()
