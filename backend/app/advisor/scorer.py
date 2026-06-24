"""
Pure-Python plot scoring for the goal-based AI Advisor.

Scores each plot 0–10 based on how well it matches the user's goal and preferences.
Hard-fails (returns 0.0) plots that violate non-negotiable constraints.
The top-N plots are forwarded to the AI for narrative reasoning.
"""

from __future__ import annotations

from app.models import Plot
from app.advisor.schemas import GoalKey, GoalPreferences

# Number of top plots sent to the AI prompt

TOP_N = 10


def score_plot_for_goal(
    plot: Plot,
    goal: GoalKey,
    prefs: GoalPreferences,
) -> float:
    """
    Score a single plot for a given goal and set of preferences.

    Returns:
        float: 0.0 if disqualified by a hard constraint, else 0.0–10.0
    """
    score = 10.0

    # Hard filters — disqualifying constraints (score = 0)

    # Over budget
    if prefs.budget_max is not None and plot.price > prefs.budget_max:
        return 0.0

    # Too small
    if prefs.min_acres is not None and plot.area_acres < prefs.min_acres:
        return 0.0

    # Commercial zoning required but plot has wrong zoning
    if prefs.commercial_zoning_required:
        if plot.zoning_type and "commercial" not in plot.zoning_type.lower():
            return 0.0

    # Soft penalties

    # Missing required road access
    if prefs.road_access_required and not plot.road_access:
        score -= 3.0

    # Missing each required utility
    _utility_map = {
        "water": plot.water_access,
        "electricity": plot.electricity,
        "sewer": plot.sewer,
    }
    for utility in prefs.utilities_required:
        if not _utility_map.get(utility, False):
            score -= 2.0

    # Missing preferred utilities (softer)
    for utility in prefs.utilities_preferred:
        if not _utility_map.get(utility, False):
            score -= 0.5

    # Location mismatch
    if prefs.preferred_location:
        loc_lower = prefs.preferred_location.strip().lower()
        plot_loc = f"{plot.city} {plot.state}".lower()
        # Match if any word in the preferred location appears in the plot location
        if not any(word in plot_loc for word in loc_lower.split()):
            score -= 2.5

    # Risk alignment
    risk_level = (plot.computed_risk_level or "Medium").lower()
    if prefs.risk_tolerance == "low" and risk_level == "high":
        score -= 3.0
    elif prefs.risk_tolerance == "low" and risk_level == "medium":
        score -= 1.0
    elif prefs.risk_tolerance == "high" and risk_level == "low":
        score -= 0.3  # Minor: low risk is never a real problem

    # Zoning preference mismatch (soft)
    if prefs.zoning_preference and plot.zoning_type:
        if prefs.zoning_preference.lower() not in plot.zoning_type.lower():
            score -= 1.5

    # Goal-specific bonuses

    appreciation = (plot.computed_appreciation or "Low").lower()
    risk_level_lower = risk_level

    if goal == GoalKey.invest_appreciation:
        bonus = {"high": 2.0, "moderate": 1.0, "low": 0.0}
        score += bonus.get(appreciation, 0.0)

    elif goal == GoalKey.maximize_value:
        if plot.area_acres > 0:
            ppa = plot.price / plot.area_acres
            if ppa < 15_000:
                score += 2.5
            elif ppa < 30_000:
                score += 1.5
            elif ppa < 50_000:
                score += 0.5
        if prefs.price_per_acre_priority:
            # Extra weight on price/acre when user explicitly asked for it
            if plot.area_acres > 0 and plot.price / plot.area_acres < 20_000:
                score += 1.0

    elif goal == GoalKey.retirement_lifestyle:
        if risk_level_lower == "low":
            score += 1.5
        if plot.road_access:
            score += 0.5
        if prefs.quiet_area and plot.ideal_for:
            if any(kw in plot.ideal_for.lower() for kw in ["quiet", "rural", "retreat", "nature"]):
                score += 1.0

    elif goal == GoalKey.build_home:
        if plot.zoning_type and "residential" in plot.zoning_type.lower():
            score += 1.5
        if plot.road_access and plot.water_access and plot.electricity:
            score += 1.0  # Fully utility-ready bonus

    elif goal == GoalKey.commercial:
        if plot.zoning_type and "commercial" in plot.zoning_type.lower():
            score += 2.0
        if plot.road_access:
            score += 1.0

    # ------------------------------------------------------------------ #
    # Existing AI insight bonus (if plot has been analyzed before)
    # ------------------------------------------------------------------ #

    if plot.insight and plot.insight.investment_score:
        # Blend in up to 1.0 extra based on the stored investment score
        score += (plot.insight.investment_score / 10.0)

    return max(0.0, min(score, 10.0))


def get_top_candidates(
    plots: list[Plot],
    goal: GoalKey,
    prefs: GoalPreferences,
    n: int = TOP_N,
) -> list[tuple[Plot, float]]:
    """
    Score all plots and return the top-N that pass hard filters,
    sorted descending by score.

    Returns:
        List of (plot, score) tuples, max length n.
    """
    scored = [
        (plot, score_plot_for_goal(plot, goal, prefs))
        for plot in plots
    ]
    # Remove hard-filtered (score == 0) and sort descending
    qualified = [(p, s) for p, s in scored if s > 0]
    qualified.sort(key=lambda x: x[1], reverse=True)
    return qualified[:n]
