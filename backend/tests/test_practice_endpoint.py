from app.main import app
from app.routers.practice import get_gemini_service
from app.services.gemini_service import PracticeTurnResult

CHAT_ID = "c3b1f7a0-6b8e-4b9b-8a3a-8f8c9a1f2e3d"


class FakeGeminiService:
    """Stand-in for GeminiService so tests never make a real network call."""

    def __init__(self, result: PracticeTurnResult | None = None, summary: str = ""):
        self._result = result
        self._summary = summary
        self.last_call_kwargs: dict | None = None

    def continue_practice_conversation(self, **kwargs) -> PracticeTurnResult:
        self.last_call_kwargs = kwargs
        return self._result

    def summarize_conversation(self, **kwargs) -> str:
        self.last_call_kwargs = kwargs
        return self._summary


def _override_gemini(result: PracticeTurnResult | None = None, summary: str = "") -> FakeGeminiService:
    fake = FakeGeminiService(result, summary)
    app.dependency_overrides[get_gemini_service] = lambda: fake
    return fake


def test_practice_turn_returns_tutor_reply(client):
    _override_gemini(PracticeTurnResult(tutor_reply="Nice to meet you! Where are you from?"))

    response = client.post(
        "/api/v1/practice/turn",
        json={"chat_id": CHAT_ID, "topic": "Greetings & Introductions", "learner_message": "My name is Ravi."},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {
        "tutor_reply": "Nice to meet you! Where are you from?",
        "correction": None,
        "native_note": None,
        "conversation_summary": None,
        "summarized_through_index": 0,
    }


def test_practice_turn_passes_topic_and_history_through(client):
    fake = _override_gemini(PracticeTurnResult(tutor_reply="Great! What else?"))

    response = client.post(
        "/api/v1/practice/turn",
        json={
            "chat_id": CHAT_ID,
            "topic": "Food & Ordering",
            "history": [
                {"speaker": "tutor", "text": "Welcome! What would you like to order?"},
                {"speaker": "learner", "text": "I would like a cup of coffee."},
            ],
            "learner_message": "And some bread too.",
            "preferred_address_term": "Nanna",
            "native_language": "Telugu",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert fake.last_call_kwargs["topic"] == "Food & Ordering"
    assert len(fake.last_call_kwargs["history"]) == 2
    assert fake.last_call_kwargs["learner_message"] == "And some bread too."
    assert fake.last_call_kwargs["preferred_address_term"] == "Nanna"
    assert fake.last_call_kwargs["native_language"] == "Telugu"


def test_practice_turn_rejects_empty_topic(client):
    response = client.post(
        "/api/v1/practice/turn",
        json={"chat_id": CHAT_ID, "topic": "", "learner_message": "Hello!"},
    )

    assert response.status_code == 422


def test_practice_turn_rejects_missing_topic(client):
    response = client.post(
        "/api/v1/practice/turn",
        json={"chat_id": CHAT_ID, "learner_message": "Hello!"},
    )

    assert response.status_code == 422


def test_practice_turn_rejects_empty_learner_message(client):
    response = client.post(
        "/api/v1/practice/turn",
        json={"chat_id": CHAT_ID, "topic": "Small Talk With Strangers", "learner_message": ""},
    )

    assert response.status_code == 422


def test_practice_turn_rejects_missing_chat_id(client):
    response = client.post(
        "/api/v1/practice/turn",
        json={"topic": "Small Talk With Strangers", "learner_message": "Hello!"},
    )

    assert response.status_code == 422


def test_practice_turn_returns_correction_and_native_note(client):
    _override_gemini(
        PracticeTurnResult(
            tutor_reply="That's alright, tell me more!",
            correction="We usually say 'I went' instead of 'I go' for yesterday.",
            native_note="నిన్నటి గురించి చెప్పేటప్పుడు 'I go' కాదు 'I went' అనాలి.",
        )
    )

    response = client.post(
        "/api/v1/practice/turn",
        json={"chat_id": CHAT_ID, "topic": "Past Events — Talking About Yesterday", "learner_message": "Yesterday I go to market."},
    )

    body = response.json()
    app.dependency_overrides.clear()
    assert body["correction"] == "We usually say 'I went' instead of 'I go' for yesterday."
    assert body["native_note"].startswith("నిన్నటి")


def test_practice_turn_passes_conversation_summary_and_index_through(client):
    fake = _override_gemini(PracticeTurnResult(tutor_reply="How is Uravakonda this time of year?"))

    response = client.post(
        "/api/v1/practice/turn",
        json={
            "chat_id": CHAT_ID,
            "topic": "Small Talk With Strangers",
            "learner_message": "It's very hot these days.",
            "conversation_summary": "The learner is from Uravakonda and has two children.",
            "summarized_through_index": 8,
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert fake.last_call_kwargs["conversation_summary"] == "The learner is from Uravakonda and has two children."
    assert fake.last_call_kwargs["summarized_through_index"] == 8


def test_practice_turn_returns_updated_summary_state_from_the_service(client):
    _override_gemini(
        PracticeTurnResult(
            tutor_reply="Got it!",
            conversation_summary="The learner is from Uravakonda.",
            summarized_through_index=10,
        )
    )

    response = client.post(
        "/api/v1/practice/turn",
        json={"chat_id": CHAT_ID, "topic": "Small Talk With Strangers", "learner_message": "Hello again."},
    )

    body = response.json()
    assert body["conversation_summary"] == "The learner is from Uravakonda."
    assert body["summarized_through_index"] == 10


def test_summarize_conversation_returns_summary(client):
    _override_gemini(summary="The learner is from Uravakonda and works as a teacher.")

    response = client.post(
        "/api/v1/practice/summarize",
        json={
            "history": [
                {"speaker": "tutor", "text": "Where are you from?"},
                {"speaker": "learner", "text": "I am from Uravakonda."},
            ],
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"summary": "The learner is from Uravakonda and works as a teacher."}


def test_summarize_conversation_passes_previous_summary_through(client):
    fake = _override_gemini(summary="updated summary")

    response = client.post(
        "/api/v1/practice/summarize",
        json={
            "history": [{"speaker": "learner", "text": "I also have a daughter."}],
            "previous_summary": "The learner is from Uravakonda.",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert fake.last_call_kwargs["previous_summary"] == "The learner is from Uravakonda."


def test_summarize_conversation_rejects_empty_history(client):
    response = client.post("/api/v1/practice/summarize", json={"history": []})

    assert response.status_code == 422
