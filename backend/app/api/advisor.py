from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.advisor.feedback_mapper import (
    FEEDBACK_LABELS,
    apply_feedback_to_preferences,
    create_session,
    get_session,
    is_no_op_feedback,
    update_session_recommendation,
)
from app.advisor.recommendation_service import (
    # ADK 2.0 graph workflow entry points — replace direct service calls.
    # The originals (run_goal_recommendation, run_refine_recommendation) remain
    # in recommendation_service.py for reference and backward compatibility.
    run_goal_recommendation_via_workflow,
    run_refine_recommendation_via_workflow,
)
from app.advisor.schemas import (
    AdvisorDecisionTrace,
    AdvisorRecommendation,
    AlternativeItem,
    FeedbackRequest,
    PlotRecommendationItem,
    RecommendRequest,
)
from app.database import get_db
from app.models import Plot
from app.services.advisor_service import (
    advisor_preflight_notices,
    advisor_runtime_error_detail,
)

router = APIRouter()


@router.post("/advisor/recommend", response_model=AdvisorRecommendation)
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

    notices = advisor_preflight_notices(plots, request.goal, request.preferences)

    try:
        # ADK 2.0 graph workflow — routes through fast_recommendation or
        # specialist_review before calling Gemini. Debug logs show route_taken,
        # top_score, score_gap, and reason_for_route (never sent to frontend).
        result = run_goal_recommendation_via_workflow(
            goal=request.goal,
            preferences=request.preferences,
            plots=plots,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail= advisor_runtime_error_detail(e))

    shortlisted_ids = [plot["plot_id"] for plot in result.get("recommended_plots", [])]
    recommendation = AdvisorRecommendation(
        recommended_plots=[
            PlotRecommendationItem(**plot)
            for plot in result.get("recommended_plots", [])
        ],
        primary_recommendation=PlotRecommendationItem(
            **result["primary_recommendation"]
        ),
        confidence=result.get("confidence", 0.5),
        notices=notices,
        reasoning=result.get("reasoning", []),
        risks=result.get("risks", []),
        tradeoffs=result.get("tradeoffs", []),
        alternatives=[
            AlternativeItem(**alternative)
            for alternative in result.get("alternatives", [])
        ],
        next_steps=result.get("next_steps", []),
        decision_trace=(
            AdvisorDecisionTrace(**result["decision_trace"])
            if result.get("decision_trace")
            else None
        ),
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


@router.post("/advisor/feedback", response_model=AdvisorRecommendation)
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

    notices = advisor_preflight_notices(plots, session.goal, updated_prefs)

    try:
        # ADK 2.0 graph workflow — feedback refinement always routes through
        # specialist_review (models HITL re-entry: user corrected → re-evaluate).
        result = run_refine_recommendation_via_workflow(
            goal=session.goal,
            updated_preferences=updated_prefs,
            plots=plots,
            feedback_label=feedback_label,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=advisor_runtime_error_detail(e))

    refined = AdvisorRecommendation(
        recommended_plots=[
            PlotRecommendationItem(**plot)
            for plot in result.get("recommended_plots", [])
        ],
        primary_recommendation=PlotRecommendationItem(
            **result["primary_recommendation"]
        ),
        confidence=result.get("confidence", 0.5),
        notices=notices,
        reasoning=result.get("reasoning", []),
        risks=result.get("risks", []),
        tradeoffs=result.get("tradeoffs", []),
        alternatives=[
            AlternativeItem(**alternative)
            for alternative in result.get("alternatives", [])
        ],
        next_steps=result.get("next_steps", []),
        decision_trace=(
            AdvisorDecisionTrace(**result["decision_trace"])
            if result.get("decision_trace")
            else None
        ),
        session_token=request.session_token,
    )

    update_session_recommendation(
        token=request.session_token,
        feedback=feedback,
        new_recommendation=refined,
        updated_preferences=updated_prefs,
    )
    return refined
