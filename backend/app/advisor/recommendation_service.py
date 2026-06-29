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

        data = json.loads(response.text)
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

        return json.loads(response.text)

    except Exception as e:
        raise RuntimeError(f"AI refinement failed: {e}") from e
