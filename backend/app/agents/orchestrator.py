from google.adk.agents import SequentialAgent

from app.agents.config import configure_google
from app.agents.specialists import (
    ai_search_agent,
    ai_search_ranking_explainer_agent,
)

configure_google()

ai_search_orchestrator = SequentialAgent(
    name="ai_search_orchestrator",
    sub_agents=[
        ai_search_agent,
        ai_search_ranking_explainer_agent,
    ],
)

root_agent = ai_search_orchestrator
ai_search_root_agent = ai_search_orchestrator
