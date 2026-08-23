# Uccharan — AI English Speaking Tutor

Monorepo containing the Android app and its backend API.

```
uccharan/
├── android/    Kotlin + Jetpack Compose app (package: com.uccharan.app)
└── backend/    FastAPI service — talks to Gemini, deployed on Render
```

## Backend — local setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GOOGLE_API_KEY from https://aistudio.google.com
uvicorn app.main:app --reload
```

Run tests:

```bash
cd backend
pytest
```

## Android app

Open `android/` in Android Studio, let Gradle sync, then Run on an emulator or device.

The backend URL the app calls is `BACKEND_BASE_URL` in `android/app/build.gradle.kts`.

## Testing on a physical device before Render is deployed

A physical phone can't reach your laptop's `localhost`. Until the backend is
deployed to Render, tunnel it instead:

```bash
# Terminal 1 — run the backend (pick a free port; 8000 is often taken by other local services)
cd backend && source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8471

# Terminal 2 — tunnel it publicly
cloudflared tunnel --protocol http2 --edge-ip-version 4 --url http://localhost:8471
```

(`--protocol http2 --edge-ip-version 4` are needed on networks that block QUIC/UDP
or don't have real IPv6 routing — common on corporate networks. Plain `ngrok`
may fail outright on such networks due to certificate pinning; `cloudflared`
was the one that worked here.)

Copy the `https://*.trycloudflare.com` URL it prints into `BACKEND_BASE_URL`
in `android/app/build.gradle.kts`, rebuild. **This URL changes every restart**
— it's a stopgap for testing, not a permanent backend.
