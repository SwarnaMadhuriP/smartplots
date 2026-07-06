from app.agents.prompts import AI_SEARCH_RANKING_EXPLAINER_PROMPT
from app.agents.prompts import AI_SEARCH_AGENT_PROMPT
from google.adk.agents import Agent

from app.agents.callbacks import init_planner_state
from app.tools.search_tools import semantic_search_and_score_plots

ai_search_agent = Agent(
    name="ai_search_agent",
    model="gemini-2.5-flash",
    instruction=AI_SEARCH_AGENT_PROMPT,
    tools=[semantic_search_and_score_plots],
    before_agent_callback=init_planner_state,
)


ai_search_ranking_explainer_agent = Agent(
    name="ai_search_ranking_explainer_agent",
    model="gemini-2.5-flash",
    instruction=AI_SEARCH_RANKING_EXPLAINER_PROMPT,
)
