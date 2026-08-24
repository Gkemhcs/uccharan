from app.services.gemini_service import GeminiService, PracticeMessage


def test_parse_practice_response_extracts_reply_only():
    result = GeminiService._parse_practice_response(
        "REPLY: Nice to meet you! Where are you from?\nCORRECTION: NONE"
    )

    assert result.tutor_reply == "Nice to meet you! Where are you from?"
    assert result.correction is None
    assert result.native_note is None


def test_parse_practice_response_extracts_correction_and_native_note():
    result = GeminiService._parse_practice_response(
        "REPLY: That's alright, tell me more!\n"
        "CORRECTION: We usually say 'I went' instead of 'I go' for yesterday.\n"
        "NATIVE_NOTE: 'I go' kaadu, 'I went' anali."
    )

    assert result.correction == "We usually say 'I went' instead of 'I go' for yesterday."
    assert result.native_note == "'I go' kaadu, 'I went' anali."


def test_parse_practice_response_is_case_insensitive_on_labels():
    result = GeminiService._parse_practice_response("reply: Hello there!\ncorrection: none")

    assert result.tutor_reply == "Hello there!"
    assert result.correction is None


def test_parse_practice_response_falls_back_gracefully_on_malformed_output():
    result = GeminiService._parse_practice_response("the model said something unexpected")

    assert "say that again" in result.tutor_reply
    assert result.correction is None


def test_parse_practice_response_reply_containing_a_colon_is_not_truncated():
    result = GeminiService._parse_practice_response("REPLY: What would you like: tea or coffee?")

    assert result.tutor_reply == "What would you like: tea or coffee?"


def test_continue_practice_conversation_includes_scenario_history_and_address_in_prompt(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="REPLY: Nice! What did you order?\nCORRECTION: NONE")
    mock_generate = mocker.patch.object(service._client.models, "generate_content", return_value=fake_response)

    service.continue_practice_conversation(
        topic="Food & Ordering",
        history=[PracticeMessage(speaker="tutor", text="Welcome! What would you like?")],
        learner_message="I would like a cup of coffee.",
        preferred_address_term="Nanna",
        native_language="Telugu",
    )

    sent_prompt = mock_generate.call_args.kwargs["contents"]
    assert "Food & Ordering" in sent_prompt
    assert "Welcome! What would you like?" in sent_prompt
    assert "I would like a cup of coffee." in sent_prompt
    assert "Nanna" in sent_prompt
    assert "NATIVE_NOTE" in sent_prompt


def test_continue_practice_conversation_includes_summary_when_given(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="REPLY: How is Uravakonda this time of year?\nCORRECTION: NONE")
    mock_generate = mocker.patch.object(service._client.models, "generate_content", return_value=fake_response)

    service.continue_practice_conversation(
        topic="Small Talk With Strangers",
        history=[],
        learner_message="It's very hot these days.",
        conversation_summary="The learner is from Uravakonda and has two children.",
    )

    sent_prompt = mock_generate.call_args.kwargs["contents"]
    assert "The learner is from Uravakonda and has two children." in sent_prompt


def test_continue_practice_conversation_caps_history_sent_to_the_model(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="REPLY: Okay!\nCORRECTION: NONE")
    mock_generate = mocker.patch.object(service._client.models, "generate_content", return_value=fake_response)

    long_history = [
        PracticeMessage(speaker="learner" if i % 2 == 0 else "tutor", text=f"message-{i}") for i in range(20)
    ]
    service.continue_practice_conversation(
        topic="Small Talk With Strangers",
        history=long_history,
        learner_message="latest message",
    )

    sent_prompt = mock_generate.call_args.kwargs["contents"]
    # Only the most recent window should appear — the earliest messages must be dropped.
    assert "message-0" not in sent_prompt
    assert "message-19" in sent_prompt


def test_continue_practice_conversation_auto_summarizes_once_history_grows_large(mocker):
    """The client never decides when to summarize — continue_practice_conversation does, in one call."""
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    summary_response = mocker.Mock(text="SUMMARY: The learner is from Uravakonda.")
    reply_response = mocker.Mock(text="REPLY: Got it!\nCORRECTION: NONE")
    mock_generate = mocker.patch.object(
        service._client.models, "generate_content", side_effect=[summary_response, reply_response]
    )

    long_history = [
        PracticeMessage(speaker="learner" if i % 2 == 0 else "tutor", text=f"message-{i}") for i in range(20)
    ]
    result = service.continue_practice_conversation(
        topic="Small Talk With Strangers",
        history=long_history,
        learner_message="latest message",
        summarized_through_index=0,
    )

    assert mock_generate.call_count == 2
    summarize_prompt = mock_generate.call_args_list[0].kwargs["contents"]
    reply_prompt = mock_generate.call_args_list[1].kwargs["contents"]

    # The summarize call covers exactly the un-windowed middle portion (indices 0..13, since
    # the last 6 stay in the raw window and never need summarizing).
    assert "message-0" in summarize_prompt
    assert "message-13" in summarize_prompt
    assert "message-14" not in summarize_prompt

    assert "The learner is from Uravakonda." in reply_prompt
    assert "message-14" in reply_prompt  # still in the raw recent window

    assert result.conversation_summary == "The learner is from Uravakonda."
    assert result.summarized_through_index == 14


def test_continue_practice_conversation_does_not_summarize_short_conversations(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="REPLY: Okay!\nCORRECTION: NONE")
    mock_generate = mocker.patch.object(service._client.models, "generate_content", return_value=fake_response)

    short_history = [PracticeMessage(speaker="learner", text=f"message-{i}") for i in range(5)]
    result = service.continue_practice_conversation(
        topic="Small Talk With Strangers",
        history=short_history,
        learner_message="latest message",
    )

    assert mock_generate.call_count == 1  # no extra summarize call
    assert result.conversation_summary is None
    assert result.summarized_through_index == 0


def test_continue_practice_conversation_does_not_re_summarize_already_covered_history(mocker):
    """A conversation that's already fully summarized shouldn't keep re-triggering just because it's long."""
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="REPLY: Okay!\nCORRECTION: NONE")
    mock_generate = mocker.patch.object(service._client.models, "generate_content", return_value=fake_response)

    # 20 messages, but the first 14 are already summarized — only 6 un-summarized,
    # which sits at the raw window boundary and shouldn't trigger another pass.
    history = [PracticeMessage(speaker="learner", text=f"message-{i}") for i in range(20)]
    result = service.continue_practice_conversation(
        topic="Small Talk With Strangers",
        history=history,
        learner_message="latest message",
        conversation_summary="Existing summary.",
        summarized_through_index=14,
    )

    assert mock_generate.call_count == 1
    assert result.conversation_summary == "Existing summary."
    assert result.summarized_through_index == 14


def test_parse_summary_response_extracts_summary_line():
    result = GeminiService._parse_summary_response(
        "SUMMARY: The learner is from Uravakonda and has two children.", fallback=""
    )

    assert result == "The learner is from Uravakonda and has two children."


def test_parse_summary_response_falls_back_to_previous_summary_on_malformed_output():
    result = GeminiService._parse_summary_response(
        "the model said something unexpected", fallback="The learner is from Uravakonda."
    )

    assert result == "The learner is from Uravakonda."


def test_summarize_conversation_sends_history_and_previous_summary_to_the_model(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="SUMMARY: The learner is from Uravakonda and has a daughter.")
    mock_generate = mocker.patch.object(service._client.models, "generate_content", return_value=fake_response)

    result = service.summarize_conversation(
        history=[PracticeMessage(speaker="learner", text="I also have a daughter.")],
        previous_summary="The learner is from Uravakonda.",
    )

    sent_prompt = mock_generate.call_args.kwargs["contents"]
    assert "The learner is from Uravakonda." in sent_prompt
    assert "I also have a daughter." in sent_prompt
    assert result == "The learner is from Uravakonda and has a daughter."


def test_summarize_conversation_returns_fallback_when_model_gives_malformed_output(mocker):
    settings = mocker.Mock(google_api_key="test-key", gemini_model="gemini-3.6-flash")
    service = GeminiService(settings)

    fake_response = mocker.Mock(text="not the expected format")
    mocker.patch.object(service._client.models, "generate_content", return_value=fake_response)

    result = service.summarize_conversation(
        history=[PracticeMessage(speaker="learner", text="hello")],
        previous_summary="The learner is from Uravakonda.",
    )

    assert result == "The learner is from Uravakonda."
