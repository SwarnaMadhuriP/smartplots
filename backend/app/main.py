from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, get_db
from .models import Plot, apply_plot_search_filters
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Literal
from app.prompts import ANALYZE_PROMPT
from google import genai
from dotenv import load_dotenv
import os
import json
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
from app.agent import root_agent
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


@app.get("/plots")
def get_plots(search: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Plot)
    if search:
        query = apply_plot_search_filters(query, search)
    plots = query.all()
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


class AnalyzeRequest(BaseModel):
    question: str | None = None


class AnalysisSchema(BaseModel):
    investment_score: int = Field(..., description="Investment score between 0 and 10")
    risk_level: Literal["Low", "Medium", "High"]
    growth_potential: Literal["Low", "Medium", "High"]
    summary: str
    reasons: List[str]
    pros: List[str]
    cons: List[str]


@app.post("/plots/{plot_id}/analyze")
def analyze_plot(plot_id: int, request: AnalyzeRequest, db: Session = Depends(get_db)):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    question = request.question or "Analyze this plot for investment potential."
    price_per_acre = plot.price / plot.area_acres if plot.area_acres > 0 else None

    prompt = ANALYZE_PROMPT.format(
        question=question,
        title=plot.title,
        city=plot.city,
        state=plot.state,
        price=plot.price,
        area=plot.area_acres,
        price_per_acre=price_per_acre if price_per_acre else "N/A",
        zoning=plot.zoning_type or "N/A",
        road="Yes" if plot.road_access else "No",
        water="Yes" if plot.water_access else "No",
        electricity="Yes" if plot.electricity else "No",
        sewer="Yes" if plot.sewer else "No",
        ideal_for=plot.ideal_for or "N/A",
        risk_notes=plot.risk_notes or "N/A",
    )

    try:
        from google.genai import types

        genai_client = get_genai_client()
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalysisSchema,
                temperature=0.2,
            ),
        )
        if response.text is None:
            raise ValueError("Response text is empty")
        data = json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "plot_id": plot.id,
        "investment_score": data.get("investment_score"),
        "risk_level": data.get("risk_level"),
        "growth_potential": data.get("growth_potential"),
        "summary": data.get("summary"),
        "reasons": data.get("reasons", []),
        "pros": data.get("pros", []),
        "cons": data.get("cons", []),
    }


class SmartSearchRequest(BaseModel):
    query: str


@app.post("/ai/search")
async def ai_search(request: SmartSearchRequest):
    session_id = str(uuid.uuid4())
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="user", session_id=session_id
    )
    runner = Runner(agent=root_agent, app_name="app", session_service=session_service)

    response_text = ""
    try:
        async for event in runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=adk_types.Content(
                role="user", parts=[adk_types.Part.from_text(text=request.query)]
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text or ""
    except Exception as e:
        print(f"Error during agent pipeline execution: {e}")
        response_text = "Rate Limiting Exceeded - Please try again in 20-30 seconds"

    session = await session_service.get_session(
        app_name="app", user_id="user", session_id=session_id
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    ranked_plots = session.state.get("ranked_plots", [])
    filters = session.state.get("filters", {})

    return {
        "response": response_text,
        "plots": ranked_plots,
        "filters": filters,
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
        primary_recommendation=PlotRecommendationItem(**result["primary_recommendation"]),
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


def _advisor_preflight_notices(plots: list[Plot], preferences: GoalPreferences) -> list[str]:
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
        return "Daily AI quota reached. Please try again tomorrow or upgrade your API key."

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
        primary_recommendation=PlotRecommendationItem(**result["primary_recommendation"]),
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
