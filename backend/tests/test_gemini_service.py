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
