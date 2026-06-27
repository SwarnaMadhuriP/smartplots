from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.agents.callback_context import CallbackContext
from app.database import SessionLocal
from app.models import Plot, DocumentChunk
from app.search import PlotSearchFilters, search_plots
from app.portfolio_agents import get_genai_client
from app.analysis_tools import (
    build_catalog_analysis,
    calculate_investment_metrics,
    calculate_location_metrics,
    calculate_risk_metrics,
)


def search_and_score_plots(
    query: str = "",
    keyword: str | None = None,
    city: str | None = None,
    state: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_area: float | None = None,
    max_area: float | None = None,
    zoning_type: str | None = None,
    listing_type: str | None = None,
    status: str | None = None,
    road_access: bool | None = None,
    water_access: bool | None = None,
    electricity: bool | None = None,
    sewer: bool | None = None,
    purpose: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict:
    """Searches for land plots using deterministic filters and ranks results for AI Search.

    This function is intentionally lightweight:
    - No investment analysis
    - No risk analysis
    - No location analysis
    - No document intelligence
    - No A2A

    The LLM should only explain the ranking later. It should not calculate scores.
    """
    db = SessionLocal()

    try:
        filters = PlotSearchFilters(
            keyword=keyword,
            city=city,
            state=state,
            min_price=min_price,
            max_price=max_price,
            min_area=min_area,
            max_area=max_area,
            zoning_type=zoning_type,
            listing_type=listing_type,
            status=status,
            road_access=road_access,
            water_access=water_access,
            electricity=electricity,
            sewer=sewer,
        )

        plots_from_db = search_plots(db, filters)
        ranked_plots = []

        for plot in plots_from_db:
            d = plot.to_json_dict()

            # Keep matchScore deterministic from plot.to_json_dict/search layer.
            # Add small purpose-based boost only when the query has clear intent.
            if purpose:
                purpose_lower = purpose.lower().strip()
                ideal_for = (plot.ideal_for or "").lower()

                if purpose_lower and purpose_lower in ideal_for:
                    d["matchScore"] = min(10, int(d.get("matchScore", 0)) + 1)

                    reason = f"Matches your {purpose_lower} preference"
                    existing_reasons = d.get("reasons", [])

                    if reason not in existing_reasons:
                        d["reasons"] = [reason] + existing_reasons[:2]

            d.update(
                {
                    "city": plot.city,
                    "state": plot.state,
                    "rawPrice": plot.price,
                    "rawAcres": plot.area_acres,
                    "createdAt": (
                        plot.created_at.isoformat() if plot.created_at else None
                    ),
                }
            )

            ranked_plots.append(d)

        ranked_plots.sort(
            key=lambda p: int(p.get("matchScore", 0)),
            reverse=True,
        )

        active_filters = {
            "keyword": keyword,
            "city": city,
            "state": state,
            "min_price": min_price,
            "max_price": max_price,
            "min_area": min_area,
            "max_area": max_area,
            "zoning_type": zoning_type,
            "listing_type": listing_type,
            "status": status,
            "road_access": road_access,
            "water_access": water_access,
            "electricity": electricity,
            "sewer": sewer,
            "purpose": purpose,
        }

        active_filters = {
            key: value
            for key, value in active_filters.items()
            if value not in (None, "")
        }

        if tool_context:
            tool_context.state["ranked_plots"] = ranked_plots
            tool_context.state["filters"] = active_filters
            tool_context.state["query"] = query

            # Keep this key only for backward compatibility.
            # AI Search should not depend on it.
            tool_context.state["deterministic_analysis"] = {}

        return {
            "status": "success",
            "count": len(ranked_plots),
        }

    finally:
        db.close()


def _ranked_plot_ids_from_state(tool_context: ToolContext | None) -> list[int]:
    if not tool_context:
        return []
    ranked_plots = tool_context.state.get("ranked_plots", [])
    return [
        int(plot["id"])
        for plot in ranked_plots
        if isinstance(plot, dict) and plot.get("id") is not None
    ]


def _plots_by_ids(plot_ids: list[int]) -> list[Plot]:
    if not plot_ids:
        return []
    db = SessionLocal()
    try:
        plots = db.query(Plot).filter(Plot.id.in_(plot_ids)).all()
        order = {plot_id: index for index, plot_id in enumerate(plot_ids)}
        return sorted(plots, key=lambda plot: order.get(plot.id, len(order)))
    finally:
        db.close()


def calculate_investment_analysis(
    tool_context: ToolContext | None = None,
) -> dict:
    """Calculates deterministic investment metrics for the current ranked plots."""
    plot_ids = _ranked_plot_ids_from_state(tool_context)
    plots = _plots_by_ids(plot_ids)
    filters = tool_context.state.get("filters", {}) if tool_context else {}
    max_budget = filters.get("max_price") if isinstance(filters, dict) else None

    metrics = [
        calculate_investment_metrics(plot, max_budget=max_budget) for plot in plots
    ]
    if tool_context:
        tool_context.state["investment_metrics"] = metrics
    return {"status": "success", "investment_metrics": metrics}


def calculate_risk_analysis(tool_context: ToolContext | None = None) -> dict:
    """Calculates deterministic risk metrics for the current ranked plots."""
    plots = _plots_by_ids(_ranked_plot_ids_from_state(tool_context))
    metrics = [calculate_risk_metrics(plot) for plot in plots]
    if tool_context:
        tool_context.state["risk_metrics"] = metrics
    return {"status": "success", "risk_metrics": metrics}


def calculate_location_analysis(tool_context: ToolContext | None = None) -> dict:
    """Calculates deterministic location metrics for the current ranked plots."""
    plots = _plots_by_ids(_ranked_plot_ids_from_state(tool_context))
    filters = tool_context.state.get("filters", {}) if tool_context else {}
    purpose = filters.get("purpose") if isinstance(filters, dict) else None
    metrics = [calculate_location_metrics(plot, purpose=purpose) for plot in plots]
    if tool_context:
        tool_context.state["location_metrics"] = metrics
    return {"status": "success", "location_metrics": metrics}


def calculate_catalog_analysis(tool_context: ToolContext | None = None) -> dict:
    """Builds a combined deterministic analysis bundle for ranked plots."""
    plots = _plots_by_ids(_ranked_plot_ids_from_state(tool_context))
    filters = tool_context.state.get("filters", {}) if tool_context else {}
    max_budget = filters.get("max_price") if isinstance(filters, dict) else None
    purpose = filters.get("purpose") if isinstance(filters, dict) else None
    analysis = build_catalog_analysis(
        plots,
        max_budget=max_budget,
        purpose=purpose,
    )
    if tool_context:
        tool_context.state["combined_analysis"] = analysis
    return {"status": "success", "combined_analysis": analysis}


async def init_planner_state(callback_context: CallbackContext) -> None:
    if "ranked_plots" not in callback_context.state:
        callback_context.state["ranked_plots"] = []
    if "filters" not in callback_context.state:
        callback_context.state["filters"] = {}
    if "query" not in callback_context.state:
        callback_context.state["query"] = ""
    if "investment_analysis" not in callback_context.state:
        callback_context.state["investment_analysis"] = "N/A"
    if "risk_analysis" not in callback_context.state:
        callback_context.state["risk_analysis"] = "N/A"
    if "location_analysis" not in callback_context.state:
        callback_context.state["location_analysis"] = "N/A"
    if "document_analysis" not in callback_context.state:
        callback_context.state["document_analysis"] = "N/A"
    if "deterministic_analysis" not in callback_context.state:
        callback_context.state["deterministic_analysis"] = {}
    if "investment_metrics" not in callback_context.state:
        callback_context.state["investment_metrics"] = []
    if "risk_metrics" not in callback_context.state:
        callback_context.state["risk_metrics"] = []
    if "location_metrics" not in callback_context.state:
        callback_context.state["location_metrics"] = []


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


def retrieve_plot_documents(
    plot_id: int,
    question: str,
    tool_context: ToolContext | None = None,
) -> list[dict]:
    """Retrieves document chunks relevant to a specific plot and question.

    Args:
        plot_id: The database ID of the plot.
        question: The user query or question to search documents for.

    Returns:
        A list of dicts with document_type, filename, page_number, and text.
    """
    db = SessionLocal()
    try:
        from google.genai import types

        client = get_genai_client()
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=question,
            config=types.EmbedContentConfig(output_dimensionality=768),
        )
        if response.embeddings and len(response.embeddings) > 0:
            question_embedding = response.embeddings[0].values
        elif (
            hasattr(response, "embedding")
            and getattr(response, "embedding") is not None
        ):
            question_embedding = getattr(response, "embedding").values
        else:
            raise ValueError(
                f"Failed to generate embedding: embeddings list is empty or None in response. Response was: {response}"
            )

        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.plot_id == plot_id)
            .order_by(DocumentChunk.embedding.cosine_distance(question_embedding))
            .limit(5)
            .all()
        )

        results = []
        for chunk in chunks:
            results.append(
                {
                    "document_type": chunk.document.document_type,
                    "filename": chunk.document.filename,
                    "page_number": chunk.page_number,
                    "text": chunk.chunk_text,
                }
            )
        return results
    finally:
        db.close()


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
    instruction="""You are the AI Search Ranking Explainer Agent.
    Your job is to:
    - Read the retrieved plots: {ranked_plots}
    - Read the search filters applied: {filters}
    - Read the original user query: {query}
    - Produce a concise search summary.
    - Explain why the top plots matched the user query and filters based on their ranking.
    - Do not calculate or invent scores (use only the provided matchScore).
    - Do not invent any facts about the plots.
    - Do not reference investment metrics/scores, risk analysis/scores, location analysis/scores, or documents/document intelligence. Rely only on the general plot characteristics and the user's criteria.""",
)

