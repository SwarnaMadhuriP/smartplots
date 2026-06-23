from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.agents.callback_context import CallbackContext
from app.database import SessionLocal
from app.models import Plot, DocumentChunk, apply_plot_search_filters
from app.portfolio_agents import get_genai_client


def search_and_score_plots(
    query: str,
    city: str | None = None,
    max_price: float | None = None,
    zoning: str | None = None,
    purpose: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict:
    """Searches for land plots in the database and ranks them based on user preferences.

    Args:
        query: General keywords to search for in title, description, or ideal uses.
        city: Optional city name to filter by (e.g. Austin, Dallas, Houston).
        max_price: Optional maximum price budget.
        zoning: Optional zoning type (e.g. residential, commercial, agricultural).
        purpose: Optional purpose of land use (e.g. camping, vacation, farming).

    Returns:
        A dict containing status and count of matched plots.
    """
    db = SessionLocal()
    try:
        db_query = db.query(Plot)

        # Apply structured filters if provided
        if city:
            db_query = db_query.filter(Plot.city.ilike(f"%{city}%"))
        if max_price:
            db_query = db_query.filter(Plot.price <= max_price)
        if zoning:
            db_query = db_query.filter(Plot.zoning_type.ilike(f"%{zoning}%"))

        # Keyword and criteria search parsing using shared helper
        if query:
            db_query = apply_plot_search_filters(db_query, query)

        plots_from_db = db_query.all()
        ranked_plots = []

        for plot in plots_from_db:
            d = plot.to_json_dict()

            # Apply conversational purpose boost if needed
            if purpose and purpose.lower() == "camping":
                ideal_for = (plot.ideal_for or "").lower()
                if "camping" in ideal_for:
                    d["matchScore"] = min(10, d["matchScore"] + 1)
                    if "Matches your camping preference" not in d["reasons"]:
                        d["reasons"] = ["Matches your camping preference"] + d[
                            "reasons"
                        ][:2]

            # Add specialists extra keys
            d.update(
                {
                    "city": plot.city,
                    "state": plot.state,
                    "rawPrice": plot.price,
                    "rawAcres": plot.area_acres,
                }
            )
            ranked_plots.append(d)

        # Sort by match score descending
        ranked_plots.sort(key=lambda p: p["matchScore"], reverse=True)

        if tool_context:
            tool_context.state["ranked_plots"] = ranked_plots
            tool_context.state["filters"] = {
                "city": city,
                "max_price": max_price,
                "zoning": zoning,
                "purpose": purpose,
            }
            tool_context.state["query"] = query

        return {"status": "success", "count": len(ranked_plots)}
    finally:
        db.close()


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


search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Search Agent. Your goal is to find land plots matching the user's query.
    Call the search_and_score_plots tool with the appropriate filters (query, city, max_price, zoning, purpose) extracted from the user prompt.
    Do not summarize the plots, simply execute the tool. The results will be processed by other agents.""",
    tools=[search_and_score_plots],
    before_agent_callback=init_planner_state,
)

investment_agent = Agent(
    name="investment_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Investment Agent. Review the land plots retrieved by the Search Agent.
    Retrieved Plots: {ranked_plots}
    
    Calculate investment projections, price per acre, and score comparisons. Highlight which plots offer the best financial value, return on investment (appreciation), and overall investment rating relative to the budget limit of: {filters}.""",
    output_key="investment_analysis",
)

risk_agent = Agent(
    name="risk_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Risk Agent. Review the land plots retrieved by the Search Agent.
    Retrieved Plots: {ranked_plots}
    
    Evaluate potential risks for each plot including:
    - Utility access limits (electricity, sewer, water access)
    - Zoning restrictions
    - Flooding, environmental, or other site-specific risk notes.
    Summarize critical concerns and things the buyer must verify during due diligence.""",
    output_key="risk_analysis",
)

location_agent = Agent(
    name="location_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Location Agent. Review the land plots retrieved by the Search Agent.
    Retrieved Plots: {ranked_plots}
    
    Analyze the locations (cities, states, neighborhoods) and proximity advantages. Discuss road access, landmarks, regional growth trends, and environmental settings (e.g. lakeside retreats, downtown proximity).""",
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
    
    Deliver a concise summary of the document findings with citations. If no documents exist for a plot, state that.
    Do not search plots or analyze structured databases; focus solely on the retrieved chunks.
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
    
    Create a polished, professional, and friendly response. Start by summarizing the overall suitability of the top matches. Then break down:
    1. 📈 **Investment Value & Financials** (based on Investment Agent output)
    2. ⚠️ **Critical Risks & Utilities** (based on Risk Agent output)
    3. 📍 **Location & Access Highlights** (based on Location Agent output)
    4. 📄 **Document Intelligence & Citations** (based on Document Intelligence Agent output, summarize key insights from brochures, zoning, utility reports, HOA rules, or county records, referencing appropriate document types, filenames, and page numbers)
    
    Conclude with a clear recommendation on next steps. Do not invent properties or parameters not present in the data.""",
)
