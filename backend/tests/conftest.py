import os

# Must be set before app.main is imported anywhere, since Settings() is
# constructed at import time and requires this field.
os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-pytest")

import pytest
from fastapi.testclient import TestClient

from app.core.auth import verify_firebase_token
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def _bypass_firebase_auth():
    """
    Every route under /api/v1 requires a verified Firebase ID token (see
    app.core.auth) — that's the actual behavior under test in
    tests/test_auth.py, but every OTHER test file here is testing something
    unrelated (a request shape, a Gemini prompt, an error path) and would
    otherwise need a real Firebase token on every call. Auto-applied to every
    test; test_auth.py pops this override for the specific cases it needs
    the real dependency active.
    """
    app.dependency_overrides[verify_firebase_token] = lambda: "test-uid"
    yield
    app.dependency_overrides.pop(verify_firebase_token, None)
