from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import correction, practice

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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
