from google.adk.agents import SequentialAgent, ParallelAgent

from app.agents.config import configure_google
from app.agents.specialists import (
    search_agent,
    investment_agent,
    risk_agent,
    location_agent,
    document_intelligence_agent,
    recommendation_agent,
    ai_search_agent,
    ai_search_ranking_explainer_agent,
)

configure_google()

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