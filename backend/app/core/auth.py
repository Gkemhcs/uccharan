from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.config import Settings, get_settings

# auto_error=False so a missing header reaches us as `None` (a clean 401
# below) instead of FastAPI's generic 403 from the security scheme itself.
_bearer_scheme = HTTPBearer(auto_error=False)

# Reused across requests for connection pooling; verify_firebase_token below
# already caches Google's public signing certs internally between calls, so
# this doesn't mean a network round-trip on every request.
_google_request = google_requests.Request()


def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> str:
    """
    Every /correct and /practice/* call reaches Gemini, which costs real
    money — and this backend is a public Render URL with no other gate, so
    without this it's an open tap anyone who finds the URL can run up a bill
    through. The Android app attaches its signed-in Firebase user's ID token
    as `Authorization: Bearer <token>` on every backend call (see
    BackendConfig's OkHttp interceptor); this verifies that token against
    Google's public signing keys. No service-account credentials are needed
    server-side for this — only a service account can *issue* Firebase
    tokens, but *verifying* one just needs the project id to check the
    token's audience/issuer against, which isn't a secret.

    Returns the verified Firebase uid — not used by any route today, but
    available for future per-user logging/rate-limiting.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    try:
        claims = google_id_token.verify_firebase_token(
            credentials.credentials,
            _google_request,
            audience=settings.firebase_project_id,
        )
    except Exception as exc:  # noqa: BLE001 - any failure here just means "not a valid session"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session") from exc

    uid = claims.get("sub") or claims.get("user_id") if claims else None
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")
    return uid
