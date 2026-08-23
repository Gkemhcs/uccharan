import os

# Must be set before app.main is imported anywhere, since Settings() is
# constructed at import time and requires this field.
os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-pytest")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
