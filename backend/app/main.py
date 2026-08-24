import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.errors import GeminiRateLimitedError, GeminiUnavailableError
from app.routers import correction, listening, practice

logger = logging.getLogger("uccharan")

app = FastAPI(title="Uccharan API", version="0.1.0")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(correction.router)
app.include_router(practice.router)
app.include_router(listening.router)


# --- Error handling ----------------------------------------------------------
#
# Without these, a Gemini failure (rate limited, quota exhausted, Gemini's own
# servers down) or any other unhandled exception falls through as a bare 500
# with no useful body — the Android client can't tell "wait a bit and retry"
# apart from "there's a real bug here", and neither can whoever's reading the
# app's error message off a phone screen. See app/core/errors.py.


@app.exception_handler(GeminiRateLimitedError)
def handle_gemini_rate_limited(request: Request, exc: GeminiRateLimitedError) -> JSONResponse:
    logger.warning("Gemini rate limited / quota exhausted: %s", exc)
    return JSONResponse(
        status_code=429,
        content={
            "detail": (
                "Our AI tutor is getting a lot of requests right now, or today's free usage "
                "limit may have been reached. Please wait a few minutes and try again."
            ),
        },
    )


@app.exception_handler(GeminiUnavailableError)
def handle_gemini_unavailable(request: Request, exc: GeminiUnavailableError) -> JSONResponse:
    logger.warning("Gemini service unavailable: %s", exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "Our AI tutor's own service is having trouble right now — this isn't something "
                "wrong with the app. Please try again in a few minutes."
            ),
        },
    )


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Last resort — a genuine bug, not a known/expected failure mode above.
    Logged with a full traceback for debugging; the client only ever sees a
    generic, honest message, distinguishable from the two handlers above."""
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our server while processing that. Please try again."},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
