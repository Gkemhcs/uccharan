"""
App-level exceptions for Gemini call failures, translated into specific,
honest HTTP responses instead of an opaque 500 — see the handlers registered
in app/main.py. Without this, every Gemini failure (rate limited, quota
exhausted, Gemini's own servers down) fell through as an unhandled exception,
which FastAPI turns into a bare 500 with no useful body — indistinguishable,
on the Android side, from a real bug in this backend's own code. A learner
hitting "please wait, we're getting a lot of requests" is a completely
different situation from "something broke, tell the developer" and should
read that way in the UI.
"""


class GeminiRateLimitedError(Exception):
    """Gemini returned 429 — per-minute rate limit or the free-tier daily quota exhausted. Actionable: wait and retry."""


class GeminiUnavailableError(Exception):
    """Gemini returned a 5xx — trouble on Google's side, not ours. Actionable: retry shortly."""
