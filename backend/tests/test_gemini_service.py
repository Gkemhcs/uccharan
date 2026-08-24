from app.services.gemini_service import GeminiService


def test_parse_response_marks_correct_attempt():
    result = GeminiService._parse_response("CORRECT: yes\nFEEDBACK: Great job, that was perfect!")

    assert result.is_correct is True
    assert result.feedback == "Great job, that was perfect!"


def test_parse_response_marks_incorrect_attempt():
    result = GeminiService._parse_response("CORRECT: no\nFEEDBACK: Try using past tense: 'went' not 'go'.")

    assert result.is_correct is False
    assert result.feedback == "Try using past tense: 'went' not 'go'."


def test_parse_response_is_case_insensitive_on_labels():
    result = GeminiService._parse_response("correct: YES\nfeedback: Nice work.")

    assert result.is_correct is True
    assert result.feedback == "Nice work."


def test_parse_response_falls_back_gracefully_on_malformed_output():
    result = GeminiService._parse_response("the model said something unexpected")

    assert result.is_correct is False
    assert "couldn't evaluate" in result.feedback


def test_parse_response_extracts_native_explanation_when_present():
    result = GeminiService._parse_response(
        "CORRECT: no\nFEEDBACK: Use 'went' not 'go'.\nNATIVE_EXPLANATION: 'went' vaadali, 'go' kaadu."
    )

    assert result.native_explanation == "'went' vaadali, 'go' kaadu."


def test_parse_response_native_explanation_defaults_to_none():
    result = GeminiService._parse_response("CORRECT: yes\nFEEDBACK: Perfect!")

    assert result.native_explanation is None


def test_check_pronunciation_attempt_includes_address_and_native_language_in_prompt(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="CORRECT: yes\nFEEDBACK: Great job!\nNATIVE_EXPLANATION: Bagundi!")
    mock_generate = mocker.patch.object(
        service._client.models, "generate_content", return_value=fake_response
    )

    service.check_pronunciation_attempt(
        target_sentence="I am happy.",
        spoken_text="I am happy.",
        preferred_address_term="Nanna",
        native_language="Telugu",
    )

    sent_prompt = mock_generate.call_args.kwargs["contents"]
    assert "Nanna" in sent_prompt
    assert "Telugu" in sent_prompt
    assert "NATIVE_EXPLANATION" in sent_prompt


def test_check_pronunciation_attempt_mentions_focus_sounds_in_prompt(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="CORRECT: yes\nFEEDBACK: Great job!")
    mock_generate = mocker.patch.object(
        service._client.models, "generate_content", return_value=fake_response
    )

    service.check_pronunciation_attempt(
        target_sentence="I think that is thin.",
        spoken_text="I tink dat is tin.",
        focus_sounds=["th"],
    )

    sent_prompt = mock_generate.call_args.kwargs["contents"]
    assert "th" in sent_prompt
    assert "name the specific sound" in sent_prompt


def test_check_pronunciation_attempt_omits_focus_sound_instruction_when_none_given(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="CORRECT: yes\nFEEDBACK: Great job!")
    mock_generate = mocker.patch.object(
        service._client.models, "generate_content", return_value=fake_response
    )

    service.check_pronunciation_attempt(target_sentence="I am happy.", spoken_text="I am happy.")

    sent_prompt = mock_generate.call_args.kwargs["contents"]
    assert "name the specific sound" not in sent_prompt
