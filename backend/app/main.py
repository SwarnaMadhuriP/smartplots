from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, get_db
from .models import Plot
from .models import DocumentChunk
from .search import PlotSearchFilters, extract_query_filters, search_plots
from .sorting import SortOption, sort_plot_dicts
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Any, cast as type_cast
from app.prompts import ASK_SMARTPLOTS_PROMPT
from app.analysis_tools import (
    calculate_investment_metrics,
    calculate_location_metrics,
    calculate_risk_metrics,
)
from app.routers import (
    QuestionRoute,
    SearchRoute,
    classify_question,
    classify_search_query,
    select_ask_specialists,
)
from google import genai
from dotenv import load_dotenv
import json
import os
import uuid
from app.portfolio_agents import (
    run_comparison_analysis,
    run_goal_recommendation,
    run_refine_recommendation,
)
from app.advisor.schemas import (
    GoalKey,
    FeedbackOption,
    GoalPreferences,
    RecommendRequest,
    FeedbackRequest,
    AdvisorRecommendation,
    PlotRecommendationItem,
    AlternativeItem,
)
from app.advisor.feedback_mapper import (
    create_session,
    get_session,
    update_session_recommendation,
    apply_feedback_to_preferences,
    is_no_op_feedback,
    FEEDBACK_LABELS,
)
from app.agent import ai_search_root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as adk_types


# Google GenAI client helper
def get_genai_client():
    load_dotenv()

    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True") == "True"
    # Fallback to API key if no GCP auth is found
    if use_vertex:
        try:
            import google.auth

            google.auth.default()
        except Exception:
            os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
            use_vertex = False

    if use_vertex:
        return genai.Client(vertexai=True, location="global")
    else:
        # Fallback to GEMINI_API_KEY if GOOGLE_API_KEY is not set
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not os.environ.get("GOOGLE_API_KEY") and gemini_key is not None:
            os.environ["GOOGLE_API_KEY"] = gemini_key
        return genai.Client(vertexai=False)


app = FastAPI(title="SmartPlots API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def plot_search_filters_from_query(
    search: str | None = Query(default=None, description="Keyword search alias"),
    keyword: str | None = Query(default=None),
    city: str | None = Query(default=None),
    state: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_area: float | None = Query(default=None, ge=0),
    max_area: float | None = Query(default=None, ge=0),
    zoning_type: str | None = Query(default=None),
    listing_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    road_access: bool | None = Query(default=None),
    water_access: bool | None = Query(default=None),
    electricity: bool | None = Query(default=None),
    sewer: bool | None = Query(default=None),
) -> PlotSearchFilters:
    return PlotSearchFilters(
        keyword=keyword or search,
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


@app.get("/plots")
def get_plots(
    filters: PlotSearchFilters = Depends(plot_search_filters_from_query),
    sort_by: SortOption = Query(default=SortOption.BEST_MATCH),
    db: Session = Depends(get_db),
):
    plots = search_plots(db, filters, sort_by=sort_by)
    return [plot.to_json_dict() for plot in plots]


@app.get("/plots/{plot_id}")
def get_plot(plot_id: int, db: Session = Depends(get_db)):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    return {
        "id": plot.id,
        "title": plot.title,
        "description": plot.description,
        "price": plot.price,
        "area_acres": plot.area_acres,
        "city": plot.city,
        "state": plot.state,
        "zoning_type": plot.zoning_type,
        "road_access": plot.road_access,
        "water_access": plot.water_access,
        "electricity": plot.electricity,
        "nearby_landmarks": plot.nearby_landmarks,
        "ideal_for": plot.ideal_for,
        "risk_notes": plot.risk_notes,
        "images": [img.image_url for img in plot.images],
    }




class AskRequest(BaseModel):
    question: str


def _property_context(plot: Plot) -> dict[str, Any]:
    return {
        "id": plot.id,
        "title": plot.title,
        "description": plot.description,
        "location": f"{plot.city}, {plot.state}",
        "price": plot.price,
        "area_acres": plot.area_acres,
        "zoning_type": plot.zoning_type,
        "utilities": {
            "road_access": plot.road_access,
            "water_access": plot.water_access,
            "electricity": plot.electricity,
            "sewer": plot.sewer,
        },
        "nearby_landmarks": plot.nearby_landmarks,
        "ideal_for": plot.ideal_for,
        "risk_notes": plot.risk_notes,
    }


def _run_ask_specialists(
    plot: Plot,
    question: str,
    specialists: list[QuestionRoute],
) -> dict[str, Any]:
    analysis: dict[str, Any] = {}
    purpose = question if QuestionRoute.LOCATION in specialists else None

    for specialist in specialists:
        if specialist == QuestionRoute.INVESTMENT:
            analysis["investment"] = calculate_investment_metrics(plot)
        elif specialist == QuestionRoute.RISK:
            analysis["risk"] = calculate_risk_metrics(plot)
        elif specialist == QuestionRoute.LOCATION:
            analysis["location"] = calculate_location_metrics(plot, purpose=purpose)

    return analysis


def _source_references(chunks: list[DocumentChunk]) -> list[dict[str, Any]]:
    sources = []
    seen = set()
    for chunk in chunks:
        filename = chunk.document.filename if chunk.document else "unknown"
        key = (filename, chunk.page_number)

        if key in seen:
            continue

        seen.add(key)
        text = type_cast(str, chunk.chunk_text) if chunk.chunk_text else ""
        excerpt = text[:200] + "..." if len(text) > 200 else text
        sources.append(
            {
                "filename": filename,
                "page": chunk.page_number,
                "excerpt": excerpt,
            }
        )

    return sources


def _document_context_from_chunks(chunks: list[DocumentChunk]) -> str:
    if not chunks:
        return "No uploaded document evidence was retrieved for this question."

    context_parts = []
    for chunk in chunks:
        filename = chunk.document.filename if chunk.document else "unknown"
        page = f" (page {chunk.page_number})" if chunk.page_number else ""
        context_parts.append(f"[{filename}{page}]\n{chunk.chunk_text}")
    return "\n\n---\n\n".join(context_parts)


def _retrieve_document_evidence(
    plot_id: int,
    question: str,
    db: Session,
) -> list[DocumentChunk]:
    from google.genai import types
    from pgvector.sqlalchemy import Vector
    from sqlalchemy import cast

    try:
        embed_response = get_genai_client().models.embed_content(
            model="gemini-embedding-2",
            contents=question,
            config=types.EmbedContentConfig(output_dimensionality=768),
        )
    except Exception:
        return []

    if not embed_response.embeddings:
        return []

    q_vector = embed_response.embeddings[0].values
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.plot_id == plot_id)
        .order_by(DocumentChunk.embedding.cosine_distance(cast(q_vector, Vector(768))))
        .limit(5)
        .all()
    )


def _compose_ask_answer(
    question: str,
    route: QuestionRoute,
    plot: Plot,
    chunks: list[DocumentChunk],
    specialists: list[QuestionRoute],
    specialist_analysis: dict[str, Any],
) -> str:
    from google.genai import types

    prompt = ASK_SMARTPLOTS_PROMPT.format(
        question=question,
        route=route.value,
        selected_specialists=json.dumps(
            [specialist.value for specialist in specialists],
            indent=2,
        ),
        property_context=json.dumps(_property_context(plot), indent=2),
        document_context=_document_context_from_chunks(chunks),
        specialist_context=json.dumps(specialist_analysis, indent=2),
    )

    try:
        response = get_genai_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1),
        )
        return response.text or "No answer generated."
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plots/{plot_id}/ask")
def ask_about_plot(plot_id: int, request: AskRequest, db: Session = Depends(get_db)):
    """Ask SmartPlots: property context, documents, up to two specialists, composer."""
    plot = db.query(Plot).filter(Plot.id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    question_route = classify_question(question)
    chunks = _retrieve_document_evidence(plot_id, question, db)
    specialists = select_ask_specialists(question)
    specialist_analysis = _run_ask_specialists(plot, question, specialists)
    answer = _compose_ask_answer(
        question=question,
        route=question_route,
        plot=plot,
        chunks=chunks,
        specialists=specialists,
        specialist_analysis=specialist_analysis,
    )

    return {
        "answer": answer,
        "sources": _source_references(chunks),
        "has_documents": bool(chunks),
        "route": question_route.value,
        "specialists": [specialist.value for specialist in specialists],
    }


class SmartSearchRequest(BaseModel):
    query: str


class SearchFiltersPayload(BaseModel):
    keyword: str | None = None
    city: str | None = None
    state: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_area: float | None = None
    max_area: float | None = None
    zoning_type: str | None = None
    listing_type: str | None = None
    status: str | None = None
    road_access: bool | None = None
    water_access: bool | None = None
    electricity: bool | None = None
    sewer: bool | None = None

    def to_filters(self, keyword: str | None = None) -> PlotSearchFilters:
        return PlotSearchFilters(
            keyword=keyword if keyword is not None else self.keyword,
            city=self.city,
            state=self.state,
            min_price=self.min_price,
            max_price=self.max_price,
            min_area=self.min_area,
            max_area=self.max_area,
            zoning_type=self.zoning_type,
            listing_type=self.listing_type,
            status=self.status,
            road_access=self.road_access,
            water_access=self.water_access,
            electricity=self.electricity,
            sewer=self.sewer,
        )

    def active_dict(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in self.model_dump().items()
            if value not in (None, "")
        }


class UnifiedSearchRequest(BaseModel):
    query: str = ""
    filters: SearchFiltersPayload = Field(default_factory=SearchFiltersPayload)
    sort_by: SortOption = SortOption.BEST_MATCH


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
    filters = request.filters.to_filters(keyword=query or request.filters.keyword)
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
    filters = request.filters.to_filters(keyword=query or request.filters.keyword)
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
        print(f"Error during agent pipeline execution: {e}")
        response_text = "Rate Limiting Exceeded - Please try again in 20-30 seconds"
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


@app.post("/search")
async def unified_search(
    request: UnifiedSearchRequest,
    db: Session = Depends(get_db),
):
    query = request.query.strip()
    route = classify_search_query(query)

    if route == SearchRoute.DB_SEARCH:
        return run_db_search(request, db)

    return await run_agent_search(request, db)


@app.post("/ai/search")
async def ai_search(request: SmartSearchRequest):
    unified = await run_agent_search(UnifiedSearchRequest(query=request.query))
    return {
        "response": unified["ai_summary"],
        "plots": unified["plots"],
        "filters": unified["filters"],
        "route": unified["route"],
    }


class CompareRequest(BaseModel):
    plot_ids: list[int]
    goal: str | None = None


@app.post("/plots/compare")
def compare_plots(request: CompareRequest, db: Session = Depends(get_db)):
    plots = db.query(Plot).filter(Plot.id.in_(request.plot_ids)).all()
    if not plots:
        raise HTTPException(status_code=400, detail="No plots found to compare.")
    try:
        return run_comparison_analysis(plots, request.goal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/advisor/recommend", response_model=AdvisorRecommendation)
def advisor_recommend(request: RecommendRequest, db: Session = Depends(get_db)):
    """
    Goal-based recommendation endpoint.
    1. Scores the full plot catalog with the Python scorer.
    2. Sends top candidates to Gemini with a structured prompt.
    3. Creates a session token for subsequent feedback calls.
    """
    plots = db.query(Plot).all()
    if not plots:
        raise HTTPException(status_code=400, detail="No plots in catalog.")

    notices = _advisor_preflight_notices(plots, request.preferences)

    try:
        result = run_goal_recommendation(
            goal=request.goal,
            preferences=request.preferences,
            plots=plots,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=_advisor_runtime_error_detail(e))

    shortlisted_ids = [p["plot_id"] for p in result.get("recommended_plots", [])]
    recommendation = AdvisorRecommendation(
        recommended_plots=[
            PlotRecommendationItem(**p) for p in result.get("recommended_plots", [])
        ],
        primary_recommendation=PlotRecommendationItem(
            **result["primary_recommendation"]
        ),
        confidence=result.get("confidence", 0.5),
        notices=notices,
        reasoning=result.get("reasoning", []),
        risks=result.get("risks", []),
        tradeoffs=result.get("tradeoffs", []),
        alternatives=[AlternativeItem(**a) for a in result.get("alternatives", [])],
        next_steps=result.get("next_steps", []),
        session_token="",
    )

    token = create_session(
        goal=request.goal,
        preferences=request.preferences,
        shortlisted_plot_ids=shortlisted_ids,
        recommendation=recommendation,
    )
    recommendation.session_token = token
    return recommendation


def _advisor_preflight_notices(
    plots: list[Plot], preferences: GoalPreferences
) -> list[str]:
    notices: list[str] = []
    preferred_location = preferences.preferred_location

    if preferred_location:
        location_words = preferred_location.strip().lower().split()
        has_location_match = any(
            any(word in f"{plot.city} {plot.state}".lower() for word in location_words)
            for plot in plots
        )

        if not has_location_match:
            notices.append(
                f"No exact matches found in {preferred_location}. Showing closest available alternatives instead."
            )

    return notices


def _advisor_runtime_error_detail(error: RuntimeError) -> str:
    err_str = str(error)
    err_lower = err_str.lower()

    if "quota" in err_lower or "RESOURCE_EXHAUSTED" in err_str:
        return (
            "Daily AI quota reached. Please try again tomorrow or upgrade your API key."
        )

    if (
        "503" in err_str
        or "unavailable" in err_lower
        or "overloaded" in err_lower
        or "high demand" in err_lower
        or "model is currently experiencing" in err_lower
    ):
        return "The AI advisor is temporarily busy due to high demand. Please try again in a few minutes."

    return err_str


@app.post("/advisor/feedback", response_model=AdvisorRecommendation)
def advisor_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Refines the advisor recommendation based on user feedback.
    - show_alternatives / good_recommendation: no AI call, returns existing result.
    - All other feedback: adjusts preferences, re-scores, and re-runs AI.
    """
    session = get_session(request.session_token)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please start a new recommendation.",
        )

    feedback = request.feedback

    if is_no_op_feedback(feedback):
        return session.last_recommendation

    updated_prefs = apply_feedback_to_preferences(session.preferences, feedback)
    feedback_label = FEEDBACK_LABELS.get(feedback, feedback.value)

    plots = db.query(Plot).all()
    if not plots:
        raise HTTPException(status_code=400, detail="No plots in catalog.")

    notices = _advisor_preflight_notices(plots, updated_prefs)

    try:
        result = run_refine_recommendation(
            goal=session.goal,
            updated_preferences=updated_prefs,
            plots=plots,
            feedback_label=feedback_label,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=_advisor_runtime_error_detail(e))

    refined = AdvisorRecommendation(
        recommended_plots=[
            PlotRecommendationItem(**p) for p in result.get("recommended_plots", [])
        ],
        primary_recommendation=PlotRecommendationItem(
            **result["primary_recommendation"]
        ),
        confidence=result.get("confidence", 0.5),
        notices=notices,
        reasoning=result.get("reasoning", []),
        risks=result.get("risks", []),
        tradeoffs=result.get("tradeoffs", []),
        alternatives=[AlternativeItem(**a) for a in result.get("alternatives", [])],
        next_steps=result.get("next_steps", []),
        session_token=request.session_token,
    )

    update_session_recommendation(
        token=request.session_token,
        feedback=feedback,
        new_recommendation=refined,
        updated_preferences=updated_prefs,
    )
    return refined
