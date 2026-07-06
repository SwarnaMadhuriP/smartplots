from pathlib import Path
import os
import logging

from app.database import initialize_database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine, SessionLocal
from sqlalchemy import text
from app.api import advisor, compare, plots, search, ask, feedback

UPLOADS_DIR = Path(__file__).resolve().parents[1] / "uploads"
logger = logging.getLogger(__name__)


def cors_origins() -> list[str]:
    origins = {"http://localhost:3000", "http://127.0.0.1:3000"}
    frontend_url = os.getenv("FRONTEND_URL")
    allow_origins = os.getenv("ALLOW_ORIGINS")

    if frontend_url:
        origins.add(frontend_url.rstrip("/"))
    if allow_origins:
        origins.update(
            origin.strip().rstrip("/")
            for origin in allow_origins.split(",")
            if origin.strip()
        )

    return sorted(origins)


app = FastAPI(title="SmartPlots API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_database() -> None:
    try:
        initialize_database()
        Base.metadata.create_all(bind=engine)
    except Exception:
        logger.exception(
            "Database initialization failed. The API will still start so "
            "Cloud Run can serve /health, but database-backed routes may fail."
        )

app.include_router(plots.router)
app.include_router(compare.router)
app.include_router(advisor.router)
app.include_router(search.router)
app.include_router(ask.router)
app.include_router(feedback.router)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ready"}
