import pytest
from google.genai import errors as genai_errors

from app.core.errors import GeminiRateLimitedError, GeminiUnavailableError
from app.services.gemini_service import GeminiService


def _api_error(error_cls, code: int):
    """Builds a real instance of google.genai.errors' ClientError/ServerError
    with just `.code` set — bypassing __init__, which expects a real
    requests/httpx response object we don't have in a unit test. Sufficient
    for GeminiService._generate, which only ever reads `.code`."""
    err = error_cls.__new__(error_cls)
    err.code = code
    return err


def test_generate_translates_a_429_client_error_into_rate_limited(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)
    mocker.patch.object(
        service._client.models, "generate_content", side_effect=_api_error(genai_errors.ClientError, 429),
    )

    with pytest.raises(GeminiRateLimitedError):
        service._generate("any prompt")


def test_generate_translates_a_server_error_into_unavailable(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)
    mocker.patch.object(
        service._client.models, "generate_content", side_effect=_api_error(genai_errors.ServerError, 503),
    )

    with pytest.raises(GeminiUnavailableError):
        service._generate("any prompt")


def test_generate_lets_a_non_429_client_error_surface_as_is(mocker):
    # A 400 (bad request) or 403 (bad API key) means OUR request was wrong,
    # not something the learner can fix by waiting — that's a real bug and
    # should surface as an unexpected error, not a friendly retry message.
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)
    mocker.patch.object(
        service._client.models, "generate_content", side_effect=_api_error(genai_errors.ClientError, 400),
    )

    with pytest.raises(genai_errors.ClientError):
        service._generate("any prompt")


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
