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
