import json

from google.genai import types
from pydantic import BaseModel

from app.advisor.prompt_builder import build_recommend_prompt, build_refine_prompt
from app.advisor.scorer import get_top_plots
from app.core.gemini import call_with_retry
from app.models import Plot


class GoalRecommendationOutput(BaseModel):
    """Structured AI output schema for goal-based recommendation."""

    class PlotItem(BaseModel):
        plot_id: int
        title: str
        location: str
        price: str
        acres: str
        score: float
        match_reason: str

    class AltItem(BaseModel):
        plot_id: int
        title: str
        location: str
        price: str
        acres: str
        key_differentiator: str

    recommended_plots: list[PlotItem]
    primary_recommendation: PlotItem
    confidence: float
    reasoning: list[str]
    risks: list[str]
    tradeoffs: list[str]
    alternatives: list[AltItem]
    next_steps: list[str]


def apply_system_scores_to_result(
    data: dict,
    top_plots: list[tuple[Plot, float]],
) -> dict:
    """
    Keep AI narrative choices, but force match scores to deterministic values.

    Gemini receives the system score in the prompt, but the JSON `score` field is
    still model-generated. This function prevents hallucinated match scores by
    overwriting returned scores from the Python scorer. It also backfills
    alternative plot entries into `recommended_plots` so the frontend can display
    real alternative match percentages instead of estimating them.
    """
    score_by_id = {int(plot.id): float(score) for plot, score in top_plots}

    def apply_score(item: dict | None) -> None:
        if not isinstance(item, dict):
            return
        try:
            plot_id = int(item.get("plot_id"))
        except (TypeError, ValueError):
            return
        if plot_id in score_by_id:
            item["score"] = score_by_id[plot_id]

    apply_score(data.get("primary_recommendation"))

    recommended = data.get("recommended_plots")
    if not isinstance(recommended, list):
        recommended = []
        data["recommended_plots"] = recommended

    seen_ids: set[int] = set()
    for item in recommended:
        apply_score(item)
        if isinstance(item, dict) and item.get("plot_id") is not None:
            try:
                seen_ids.add(int(item["plot_id"]))
            except (TypeError, ValueError):
                pass

    primary = data.get("primary_recommendation")
    if isinstance(primary, dict) and primary.get("plot_id") is not None:
        primary_id = int(primary["plot_id"])
        if primary_id not in seen_ids:
            recommended.insert(0, {**primary})
            seen_ids.add(primary_id)

    for alternative in data.get("alternatives", []):
        if not isinstance(alternative, dict) or alternative.get("plot_id") is None:
            continue
        plot_id = int(alternative["plot_id"])
        if plot_id not in score_by_id or plot_id in seen_ids:
            continue
        recommended.append(
            {
                "plot_id": plot_id,
                "title": alternative.get("title", ""),
                "location": alternative.get("location", ""),
                "price": alternative.get("price", ""),
                "acres": alternative.get("acres", ""),
                "score": score_by_id[plot_id],
                "match_reason": alternative.get("key_differentiator", ""),
            }
        )
        seen_ids.add(plot_id)

    return data


def run_goal_recommendation(
    goal,
    preferences,
    plots: list[Plot],
) -> dict:
    """
    Full recommendation pipeline:
    1. Python scorer filters and ranks the catalog.
    2. Top candidates are sent to Gemini with a structured prompt.
    3. Returns AdvisorRecommendation-compatible data.
    """
    top_plots = get_top_plots(plots, goal, preferences)

    if not top_plots:
        raise ValueError(
            "No plots match your criteria. Try relaxing your budget, location, or utility requirements."
        )

    prompt = build_recommend_prompt(goal, preferences, top_plots)

    try:
        response = call_with_retry(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GoalRecommendationOutput,
                temperature=0.2,
            ),
        )

        if not response.text:
            raise ValueError("AI recommendation returned empty response.")

        data = apply_system_scores_to_result(json.loads(response.text), top_plots)
        validated = GoalRecommendationOutput.model_validate(data)
        return validated.model_dump()

    except Exception as e:
        raise RuntimeError(f"AI recommendation failed: {e}") from e


def run_refine_recommendation(
    goal,
    updated_preferences,
    plots: list[Plot],
    feedback_label: str,
) -> dict:
    """
    Refinement pipeline triggered by user feedback.
    Re-scores with updated preferences, then re-runs AI with feedback context.
    """
    top_plots = get_top_plots(plots, goal, updated_preferences)

    if not top_plots:
        raise ValueError(
            "After applying your feedback, no plots match the updated criteria. "
            "Try adjusting your preferences."
        )

    prompt = build_refine_prompt(
        goal,
        updated_preferences,
        top_plots,
        feedback_label,
    )

    try:
        response = call_with_retry(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GoalRecommendationOutput,
                temperature=0.2,
            ),
        )

        if not response.text:
            raise ValueError("AI refinement returned empty response.")

        data = apply_system_scores_to_result(json.loads(response.text), top_plots)
        validated = GoalRecommendationOutput.model_validate(data)
        return validated.model_dump()

    except Exception as e:
        raise RuntimeError(f"AI refinement failed: {e}") from e


# ---------------------------------------------------------------------------
# ADK 2.0 Graph Workflow wrappers
#
# These thin functions delegate to the new graph-style workflow in workflow.py.
# They replace the direct calls in api/advisor.py while keeping the existing
# run_goal_recommendation / run_refine_recommendation functions intact for
# reference, testing, and backward compatibility.
#
# ADK 2.0 mapping: These act as the public entry points into the WorkflowAgent,
# equivalent to calling agent.run() in ADK 2.0.
# ---------------------------------------------------------------------------


def run_goal_recommendation_via_workflow(
    goal,
    preferences,
    plots: list[Plot],
) -> dict:
    """
    Run a fresh goal-based recommendation through the ADK 2.0-style graph workflow.

    Replaces direct calls to run_goal_recommendation() in api/advisor.py.
    The workflow adds deterministic routing (fast vs specialist path) before
    any Gemini call is made.
    """
    from app.advisor.workflow import run_advisor_workflow
    return run_advisor_workflow(goal=goal, preferences=preferences, plots=plots)


def run_refine_recommendation_via_workflow(
    goal,
    updated_preferences,
    plots: list[Plot],
    feedback_label: str,
) -> dict:
    """
    Run a feedback-refinement pass through the ADK 2.0-style graph workflow.

    Replaces direct calls to run_refine_recommendation() in api/advisor.py.
    The workflow always routes through specialist_review for feedback passes
    (models the ADK 2.0 HITL re-entry pattern).
    """
    from app.advisor.workflow import run_advisor_feedback_workflow
    return run_advisor_feedback_workflow(
        goal=goal,
        preferences=updated_preferences,
        plots=plots,
        feedback_label=feedback_label,
    )
