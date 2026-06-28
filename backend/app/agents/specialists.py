from app.agents.prompts import AI_SEARCH_RANKING_EXPLAINER_PROMPT
from app.agents.prompts import AI_SEARCH_AGENT_PROMPT
from google.adk.agents import Agent

from app.agents.callbacks import init_planner_state
from app.tools.search_tools import search_and_score_plots
from app.tools.analysis_tools import (
    calculate_investment_analysis,
    calculate_risk_analysis,
    calculate_location_analysis,
)
from app.tools.document_tools import retrieve_plot_documents

search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Search Agent. Your goal is to find land plots matching the user's query.
    Extract structured filters from the user prompt, then call search_and_score_plots.
    Use only supported deterministic filters: keyword, city, state, min_price, max_price,
    min_area, max_area, zoning_type, listing_type, status, road_access, water_access,
    electricity, sewer, and purpose.
    Do not pass full raw natural-language requests as keyword. Use keyword only for a
    concise searchable term such as "lake", "downtown", "camping", or "Austin".
    Do not query the database directly or invent filtering logic. Do not summarize the plots;
    simply execute the tool. The results will be processed by other agents.""",
    tools=[search_and_score_plots],
    before_agent_callback=init_planner_state,
)

ai_search_agent = Agent(
    name="ai_search_agent",
    model="gemini-2.5-flash",
    instruction=AI_SEARCH_AGENT_PROMPT,
    tools=[search_and_score_plots],
    before_agent_callback=init_planner_state,
)

investment_agent = Agent(
    name="investment_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Investment Agent. Review the land plots retrieved by the Search Agent.
    Retrieved Plots: {ranked_plots}
    Current Investment Metrics: {investment_metrics}
    
    First call calculate_investment_analysis. Then explain the returned deterministic metrics.
    Do not calculate or invent scores. Explain price per acre, budget fit, utility score,
    development readiness, investment score, pros, and cons relative to: {filters}.""",
    tools=[calculate_investment_analysis],
    output_key="investment_analysis",
)

risk_agent = Agent(
    name="risk_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Risk Agent. Review the land plots retrieved by the Search Agent.
    Retrieved Plots: {ranked_plots}
    Current Risk Metrics: {risk_metrics}
    
    First call calculate_risk_analysis. Then explain the returned deterministic metrics.
    Do not calculate or invent risk scores. Explain infrastructure risk, utility risk,
    zoning risk, overall risk score, and mitigation suggestions.""",
    tools=[calculate_risk_analysis],
    output_key="risk_analysis",
)

location_agent = Agent(
    name="location_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Location Agent. Review the land plots retrieved by the Search Agent.
    Retrieved Plots: {ranked_plots}
    Current Location Metrics: {location_metrics}
    
    First call calculate_location_analysis. Then explain the returned deterministic metrics.
    Do not calculate or invent location scores. Explain location score, nearby landmark score,
    accessibility, purpose suitability, and best use.""",
    tools=[calculate_location_analysis],
    output_key="location_analysis",
)

document_intelligence_agent = Agent(
    name="document_intelligence_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Document Intelligence Agent. Your goal is to analyze retrieved document chunks for the matched plots and answer questions from brochures, zoning docs, HOA docs, utility reports, and county records.
    
    You have access to the tool `retrieve_plot_documents(plot_id, question)`.
    
    Matched Plots: {ranked_plots}
    User Query/Question: {query}
    
    For each plot in the matched plots, you MUST query its relevant documents by calling `retrieve_plot_documents` with the plot's ID and the user query/question.
    Analyze the retrieved chunks to identify:
    - Important insights, utility details, zoning permissions, HOA constraints, or flood risks.
    - Reference specific documents, citing their type, filename, and page number.
    - Missing information that the documents do not answer.
    
    Deliver a concise summary of the document findings with citations. If no documents exist for a plot, state that.
    Do not calculate investment, risk, or location scores. Do not search plots or analyze structured databases; focus solely on the retrieved chunks.
    """,
    output_key="document_analysis",
    tools=[retrieve_plot_documents],
)


recommendation_agent = Agent(
    name="recommendation_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Recommendation Agent. Your goal is to synthesize the findings from the specialized agents and deliver the final SmartPlots Response.
    
    Data received:
    - Search Filters: {filters}
    - Found Plots: {ranked_plots}
    - Investment Analysis: {investment_analysis}
    - Risk Assessment: {risk_analysis}
    - Location Analysis: {location_analysis}
    - Document Analysis: {document_analysis}
    
    Combine the specialist analyses into a final recommendation with reasoning and trade-offs.
    Do not perform new calculations or invent scores. Use only the retrieved plots, deterministic
    metric explanations, and document evidence already provided by upstream agents.
    
    Create a polished, professional, and friendly response. Start by summarizing the overall suitability of the top matches. Then break down:
    1. 📈 **Investment Value & Financials** (based on Investment Agent output)
    2. ⚠️ **Critical Risks & Utilities** (based on Risk Agent output)
    3. 📍 **Location & Access Highlights** (based on Location Agent output)
    4. 📄 **Document Intelligence & Citations** (based on Document Intelligence Agent output, summarize key insights from brochures, zoning, utility reports, HOA rules, or county records, referencing appropriate document types, filenames, and page numbers)
    
    Conclude with a clear recommendation on next steps. Do not invent properties or parameters not present in the data.""",
)


ai_search_ranking_explainer_agent = Agent(
    name="ai_search_ranking_explainer_agent",
    model="gemini-2.5-flash",
    instruction=AI_SEARCH_RANKING_EXPLAINER_PROMPT
)
