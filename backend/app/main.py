from app.database import initialize_database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.api import advisor, compare, plots, search, ask

app = FastAPI(title="SmartPlots API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
initialize_database()

app.include_router(plots.router)
app.include_router(compare.router)
app.include_router(advisor.router)
app.include_router(search.router)
app.include_router(ask.router)


@app.get("/health")
def health():
    return {"status": "ok"}
