import os
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from pydantic import BaseModel

class Feedback(BaseModel):
    score: int
    user_id: str
    session_id: str
    text: str

allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# Root directory of the backend containing the app package
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
session_service_uri = None

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=False,
)
app.title = "smartplots"
app.description = "API for interacting with the SmartPlots agent"

@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    return {"status": "success"}
