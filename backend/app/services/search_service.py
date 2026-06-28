import json
import uuid
from typing import Any

from fastapi import HTTPException
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as adk_types
from sqlalchemy.orm import Session

from app.agents.orchestrator import ai_search_root_agent
from app.services.routing_service import SearchRoute, classify_search_query
from app.schemas.search import UnifiedSearchRequest
from app.repositories.plot_search_repository import PlotSearchFilters, extract_query_filters, search_plots
from app.services.sorting_service import sort_plot_dicts


def active_plot_filters(filters: PlotSearchFilters) -> dict[str, Any]:
    return {
        key: value
        for key in filters.__dataclass_fields__
        if (value := getattr(filters, key)) not in (None, "")
    }


def run_db_search(
    request: UnifiedSearchRequest,
    db: Session,
) -> dict[str, Any]:
    query = request.query.strip()
    filters = request.filters.to_filters()
    filters = extract_query_filters(query, filters)
    plots = search_plots(db, filters, sort_by=request.sort_by)
    return {
        "search_mode": "db",
        "plots": [plot.to_json_dict() for plot in plots],
        "ai_summary": None,
        "filters": active_plot_filters(filters),
    }


def run_query_filter_fallback(
    request: UnifiedSearchRequest,
    db: Session,
    message: str,
) -> dict[str, Any]:
    query = request.query.strip()
    filters = request.filters.to_filters()
    filters = extract_query_filters(query, filters)
    plots = search_plots(db, filters, sort_by=request.sort_by)
    return {
        "search_mode": "db",
        "plots": [plot.to_json_dict() for plot in plots],
        "ai_summary": message,
        "filters": active_plot_filters(filters),
        "route": SearchRoute.DB_SEARCH.value,
    }


def _agent_search_message(request: UnifiedSearchRequest) -> str:
    active_filters = request.filters.active_dict()
    return (
        "Search SmartPlots using the user's natural-language query and any "
        "structured filters below. Translate the request into supported "
        "deterministic search filters before calling search_and_score_plots.\n\n"
        f"User query: {request.query.strip()}\n"
        f"Structured filters JSON: {json.dumps(active_filters, sort_keys=True)}"
    )

# TODO:
# Debug ai_search_ranking_explainer_agent.
# If the explainer returns no final response, investigate ADK event flow
# and session state propagation.

async def run_agent_search(
    request: UnifiedSearchRequest,
    db: Session | None = None,
) -> dict[str, Any]:
    route = classify_search_query(request.query)
    session_id = str(uuid.uuid4())
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="user", session_id=session_id
    )
    runner = Runner(
        agent=ai_search_root_agent,
        app_name="app",
        session_service=session_service,
    )

    response_text = ""
    agent_failed = False
    try:
        async for event in runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=adk_types.Content(
                role="user",
                parts=[adk_types.Part.from_text(text=_agent_search_message(request))],
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text or ""
    except Exception as e:
        print(f"AI search pipeline failed: {e}")

        error = str(e).lower()

        if "429" in error or "resourceexhausted" in error or "rate" in error:
            response_text = (
                "AI explanation is temporarily unavailable because the Gemini API is rate limited. "
                "Your search results have still been retrieved and ranked."
            )
        else:
            response_text = (
                "AI explanation is temporarily unavailable. "
                "Your search results have still been retrieved."
            )

        agent_failed = True

    session = await session_service.get_session(
        app_name="app", user_id="user", session_id=session_id
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    ranked_plots = session.state.get("ranked_plots", [])
    filters = session.state.get("filters", {})
    ranked_plots = sort_plot_dicts(ranked_plots, request.sort_by)

    if agent_failed and not ranked_plots and db is not None:
        return run_query_filter_fallback(
            request,
            db,
            "AI search is temporarily unavailable, so SmartPlots used DB search filters instead.",
        )

    return {
        "search_mode": "ai",
        "plots": ranked_plots,
        "ai_summary": response_text,
        "filters": filters,
        "route": route.value,
    }
