import os
import google.auth
from google.adk.apps import App
from google.adk.agents import SequentialAgent, ParallelAgent
from app.specialists import (
    search_agent,
    investment_agent,
    risk_agent,
    location_agent,
    document_intelligence_agent,
    recommendation_agent,
    ai_search_ranking_explainer_agent,
    ai_search_agent,
)

# Handle GCP auth and environment variables gracefully
try:
    _, project_id = google.auth.default()
    if not project_id:
        project_id = "mock-project-id"
except Exception:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "mock-project-id")

os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

# Check if we should use Vertex AI or AI Studio
use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")
if use_vertex is None:
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
    else:
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "False":
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not os.environ.get("GOOGLE_API_KEY") and gemini_key is not None:
        os.environ["GOOGLE_API_KEY"] = gemini_key


smartplots_orchestrator = SequentialAgent(
    name="smartplots_orchestrator",
    sub_agents=[
        search_agent,
        ParallelAgent(
            name="analysts",
            sub_agents=[
                investment_agent,
                risk_agent,
                location_agent,
                document_intelligence_agent,
            ],
        ),
        recommendation_agent,
    ],
)

ai_search_orchestrator = SequentialAgent(
    name="ai_search_orchestrator",
    sub_agents=[
        ai_search_agent,
        ai_search_ranking_explainer_agent,
    ],
)

root_agent = smartplots_orchestrator
ai_search_root_agent = ai_search_orchestrator

app = App(
    root_agent=root_agent,
    name="app",
)
