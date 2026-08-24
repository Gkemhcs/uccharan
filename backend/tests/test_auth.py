from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.core.auth import verify_firebase_token
from app.core.config import get_settings
from app.main import app


def _drop_auth_override():
    """The autouse fixture in conftest.py stubs `verify_firebase_token` for
    every test in the suite — these tests are specifically about that real
    dependency, so they remove the stub for their own duration."""
    app.dependency_overrides.pop(verify_firebase_token, None)


def test_correct_rejects_missing_authorization_header(client):
    _drop_auth_override()

    response = client.post(
        "/api/v1/correct",
        json={"target_sentence": "I am happy.", "spoken_text": "I am happy."},
    )

    assert response.status_code == 401


def test_practice_turn_rejects_missing_authorization_header(client):
    _drop_auth_override()

    response = client.post(
        "/api/v1/practice/turn",
        json={"chat_id": "c1", "topic": "Ordering food", "learner_message": "Hi"},
    )

    assert response.status_code == 401


def test_correct_rejects_garbage_bearer_token(client):
    _drop_auth_override()

    response = client.post(
        "/api/v1/correct",
        json={"target_sentence": "I am happy.", "spoken_text": "I am happy."},
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


def test_verify_firebase_token_accepts_a_valid_token():
    fake_credentials = type("Creds", (), {"credentials": "a-valid-looking-token"})()

    with patch("app.core.auth.google_id_token.verify_firebase_token", return_value={"sub": "uid-123"}):
        uid = verify_firebase_token(credentials=fake_credentials, settings=get_settings())

    assert uid == "uid-123"


def test_verify_firebase_token_rejects_a_token_that_fails_verification():
    fake_credentials = type("Creds", (), {"credentials": "an-expired-token"})()

    with patch("app.core.auth.google_id_token.verify_firebase_token", side_effect=ValueError("expired")):
        with pytest.raises(HTTPException) as exc_info:
            verify_firebase_token(credentials=fake_credentials, settings=get_settings())

    assert exc_info.value.status_code == 401
