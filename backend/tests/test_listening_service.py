from app.services.gemini_service import GeminiService


def test_parse_listening_response_extracts_all_fields():
    raw = """PASSAGE: Excuse me, does this bus go to the railway station?
QUESTION: What is the speaker asking about?
OPTION_A: The price of a ticket
OPTION_B: Directions to the railway station
OPTION_C: What time it is
OPTION_D: Whether the bus is late
CORRECT: B
EXPLANATION: The speaker asks "does this bus go to the railway station", so they want directions."""

    result = GeminiService._parse_listening_response(raw)

    assert result.passage == "Excuse me, does this bus go to the railway station?"
    assert result.question == "What is the speaker asking about?"
    assert result.options == [
        "The price of a ticket",
        "Directions to the railway station",
        "What time it is",
        "Whether the bus is late",
    ]
    assert result.correct_option_index == 1
    assert "directions" in result.explanation.lower()


def test_parse_listening_response_is_case_insensitive_on_labels():
    raw = """passage: Hello there.
question: What did they say?
option_a: Hello there.
option_b: Goodbye.
option_c: Thank you.
option_d: Sorry.
correct: a
explanation: They greeted you."""

    result = GeminiService._parse_listening_response(raw)

    assert result.passage == "Hello there."
    assert result.correct_option_index == 0


def test_parse_listening_response_falls_back_gracefully_on_malformed_output():
    result = GeminiService._parse_listening_response("the model said something unexpected")

    assert "couldn't be generated" in result.passage
    assert result.options == []
    assert result.correct_option_index == 0


def test_parse_listening_response_falls_back_to_the_first_option_if_the_correct_one_is_missing():
    raw = """PASSAGE: Test passage.
QUESTION: Test question?
OPTION_A: First
OPTION_B: Second
CORRECT: D
EXPLANATION: Because."""

    result = GeminiService._parse_listening_response(raw)

    assert result.options == ["First", "Second"]
    assert result.correct_option_index == 0  # D never came back at all — nothing sane to point at


def test_parse_listening_response_indexes_by_position_among_present_options_not_by_letter():
    # Regression case: A and C are missing, so the surviving options are [B, D].
    # CORRECT: D must resolve to index 1 (D's position among what's actually
    # present) — not index 3 (D's position in the full "ABCD" alphabet), which
    # would point past the end of this 2-item list.
    raw = """PASSAGE: Test passage.
QUESTION: Test question?
OPTION_B: Second
OPTION_D: Fourth
CORRECT: D
EXPLANATION: Because."""

    result = GeminiService._parse_listening_response(raw)

    assert result.options == ["Second", "Fourth"]
    assert result.correct_option_index == 1


def test_generate_listening_exercise_sends_the_topic_in_the_prompt(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(
        text=(
            "PASSAGE: Test.\nQUESTION: Q?\nOPTION_A: A\nOPTION_B: B\n"
            "OPTION_C: C\nOPTION_D: D\nCORRECT: A\nEXPLANATION: Because."
        ),
    )
    mock_generate = mocker.patch.object(service._client.models, "generate_content", return_value=fake_response)

    service.generate_listening_exercise(topic="Asking for directions")

    sent_prompt = mock_generate.call_args.kwargs["contents"]
    assert "Asking for directions" in sent_prompt
