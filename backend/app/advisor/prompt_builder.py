"""Builds the AI prompt for the goal-based advisor recommendation."""

from __future__ import annotations

from app.models import Plot
from app.advisor.schemas import GoalKey, GoalPreferences
from textwrap import shorten


# Human-readable labels for goals
GOAL_LABELS: dict[GoalKey, str] = {
    GoalKey.build_home: "Build a Home",
    GoalKey.invest_appreciation: "Invest for Appreciation",
    GoalKey.retirement_lifestyle: "Retirement / Lifestyle",
    GoalKey.commercial: "Commercial Development",
    GoalKey.maximize_value: "Maximize Value",
}


def _format_preferences(goal: GoalKey, prefs: GoalPreferences) -> str:
    """Render preferences as a readable bullet list for the prompt."""
    lines: list[str] = []

    if prefs.budget_max is not None:
        lines.append(f"- Budget (max): ${prefs.budget_max:,.0f}")
    if prefs.preferred_location:
        lines.append(f"- Preferred location: {prefs.preferred_location}")
    if prefs.min_acres is not None:
        lines.append(f"- Minimum acreage: {prefs.min_acres} acres")
    if prefs.utilities_required:
        lines.append(f"- Utilities REQUIRED: {', '.join(prefs.utilities_required)}")
    if prefs.utilities_preferred:
        lines.append(f"- Utilities preferred: {', '.join(prefs.utilities_preferred)}")
    if prefs.road_access_required:
        lines.append("- Road access: required")
    if prefs.zoning_preference:
        lines.append(f"- Zoning preference: {prefs.zoning_preference}")
    if prefs.commercial_zoning_required:
        lines.append("- Commercial zoning: required")
    if prefs.risk_tolerance:
        lines.append(f"- Risk tolerance: {prefs.risk_tolerance}")
    if prefs.time_horizon:
        lines.append(f"- Investment time horizon: {prefs.time_horizon}")
    if prefs.quiet_area is not None:
        lines.append(f"- Quiet/rural area preference: {'yes' if prefs.quiet_area else 'no'}")
    if prefs.price_per_acre_priority:
        lines.append("- Priority: lowest price per acre")

    return "\n".join(lines) if lines else "- No specific preferences provided"


def _format_plot_entry(plot: Plot, score: float) -> str:
    """Render a single plot as a compact text block for the prompt."""
    ppa = (plot.price / plot.area_acres) if plot.area_acres else 0
    utilities = []
    if plot.water_access:
        utilities.append("water")
    if plot.electricity:
        utilities.append("electricity")
    if plot.sewer:
        utilities.append("sewer")

    lines = [
        f"Plot #{plot.id}: {plot.title}",
        f"  Location: {plot.city}, {plot.state}",
        f"  Price: ${plot.price:,.0f} | Size: {plot.area_acres} acres | ${ppa:,.0f}/acre",
        f"  Zoning: {plot.zoning_type or 'Unknown'} | Road access: {'Yes' if plot.road_access else 'No'}",
        f"  Utilities available: {', '.join(utilities) if utilities else 'None'}",
        f"  Risk level: {plot.computed_risk_level} | Appreciation: {plot.computed_appreciation}",
        f"  System match score: {score:.1f}/10",
    ]
    if plot.ideal_for:
        lines.append(f"  Ideal for: {plot.ideal_for}")
    if plot.risk_notes:
        lines.append(f"  Risk notes: {plot.risk_notes}")
    if plot.description:
        lines.append(
            # pyrefly: ignore [bad-argument-type]
            f"  Description: {shorten(plot.description, width=300, placeholder='...')}"
        )

    return "\n".join(lines)


def build_recommend_prompt(
    goal: GoalKey,
    preferences: GoalPreferences,
    top_plots: list[tuple[Plot, float]],
    rag_chunks: list[str] | None = None,
) -> str:
    """
    Build the full AI recommendation prompt.

    Args:
        goal: The user's selected investment/use goal.
        preferences: Goal-specific user preferences.
        top_plots: (plot, score) pairs from the Python scorer, already sorted descending.
        rag_chunks: Optional document evidence retrieved for the scored shortlist.

    Returns:
        Prompt string ready to send to Gemini.
    """
    goal_label = GOAL_LABELS.get(goal, goal.value)
    prefs_text = _format_preferences(goal, preferences)

    plots_text = "\n\n".join(
        _format_plot_entry(plot, score) for plot, score in top_plots
    )

    prompt = f"""You are SmartPlots AI Advisor, a specialist in land investment and real estate.
Your job is to recommend the single best land plot from the pre-scored shortlist below,
based on the user's goal and preferences.

CRITICAL RULES:
- Use ONLY the facts provided in the plot data below. Do NOT invent specifications, utilities, or zoning details.
- Deterministic Python scores are the source of truth. Do NOT change scores, rankings, or plot IDs.
- Document evidence is supporting context only. Use it to explain or qualify the recommendation, not to override scores.
- If document evidence is unavailable or does not address a point, say that clearly instead of inventing document facts.
- Base your recommendation on the user's goal and preferences.
- Be specific and actionable in your reasoning.
- Set confidence as a float 0.0–1.0 reflecting how well the top plot truly matches all requirements.
- If the top plot has significant drawbacks, reflect that in a lower confidence score.

=== USER GOAL ===
{goal_label}

=== USER PREFERENCES ===
{prefs_text}

=== TOP CANDIDATE PLOTS (pre-scored by system) ===
{plots_text}

=== INSTRUCTIONS ===
1. Select the single best plot as primary_recommendation.
2. Include it in recommended_plots as the first entry.
3. List 2–3 best alternatives from the remaining candidates in the alternatives array.
4. reasoning: 3–5 specific, factual bullets explaining why this plot was chosen.
5. risks: 2–4 real risks based on the data (missing utilities, risk notes, zoning mismatches).
6. tradeoffs: Compare primary vs. alternatives (e.g. "Plot B is cheaper but lacks electricity").
7. next_steps: 3–4 actionable steps the user should take next (site visit, zoning check, utility estimate, etc.).
8. confidence: 0.0–1.0. Use 0.8+ only if the plot strongly matches ALL user requirements.

Respond with valid JSON matching the response schema exactly."""

    if rag_chunks:
        doc_context = "\n\n".join(rag_chunks)
        prompt += f"""

=== RELEVANT DOCUMENT EVIDENCE ===
{doc_context}

Use the above document evidence to supplement the plot data where relevant.
Preserve source filenames and page numbers in reasoning, risks, or next steps when applicable.
If the evidence says it is unavailable, explicitly state that document evidence was unavailable and continue with plot data only."""

    return prompt


def build_refine_prompt(
    goal: GoalKey,
    updated_preferences: GoalPreferences,
    top_plots: list[tuple[Plot, float]],
    feedback_label: str,
    rag_chunks: list[str] | None = None,
) -> str:
    """
    Build a refinement prompt after the user has given feedback.
    Adds context about the previous feedback to guide the AI.
    """
    base = build_recommend_prompt(goal, updated_preferences, top_plots, rag_chunks)

    # Prepend feedback context
    feedback_section = f"""
=== USER FEEDBACK ON PREVIOUS RECOMMENDATION ===
The user said: "{feedback_label}"
Their preferences have been automatically updated. Please provide a refined recommendation
that addresses this feedback. Acknowledge the feedback briefly in your reasoning.

"""
    return feedback_section + base
