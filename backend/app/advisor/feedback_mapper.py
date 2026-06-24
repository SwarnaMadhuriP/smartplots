"""
Session store and feedback → preference adjustment logic for the AI Advisor.

Sessions are held in-memory for the MVP (single-worker dev setup).
For production/multi-server, replace _advisor_sessions with a Redis or DB backend.

Session lifetime: 30 minutes. Stale sessions are cleaned up lazily on new session creation.
"""

from __future__ import annotations

import uuid
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.advisor.schemas import (
    AdvisorRecommendation,
    FeedbackOption,
    GoalKey,
    GoalPreferences,
)

# ---------------------------------------------------------------------------
# Session storage
# ---------------------------------------------------------------------------

SESSION_TTL = timedelta(minutes=30)


@dataclass
class AdvisorSession:
    goal: GoalKey
    preferences: GoalPreferences
    shortlisted_plot_ids: list[int]
    last_recommendation: AdvisorRecommendation
    feedback_history: list[FeedbackOption] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)


# In-memory store: token → session
_advisor_sessions: dict[str, AdvisorSession] = {}


def _purge_stale_sessions() -> None:
    """Remove sessions older than SESSION_TTL. Called lazily on new session creation."""
    cutoff = datetime.utcnow() - SESSION_TTL
    stale = [token for token, s in _advisor_sessions.items() if s.last_active < cutoff]
    for token in stale:
        del _advisor_sessions[token]


def create_session(
    goal: GoalKey,
    preferences: GoalPreferences,
    shortlisted_plot_ids: list[int],
    recommendation: AdvisorRecommendation,
) -> str:
    """Create a new advisor session and return its token."""
    _purge_stale_sessions()
    token = str(uuid.uuid4())
    _advisor_sessions[token] = AdvisorSession(
        goal=goal,
        preferences=deepcopy(preferences),
        shortlisted_plot_ids=shortlisted_plot_ids,
        last_recommendation=recommendation,
    )
    return token


def get_session(token: str) -> AdvisorSession | None:
    """Retrieve a session by token. Returns None if expired or not found."""
    session = _advisor_sessions.get(token)
    if session is None:
        return None
    if datetime.utcnow() - session.last_active > SESSION_TTL:
        del _advisor_sessions[token]
        return None
    session.last_active = datetime.utcnow()
    return session


def update_session_recommendation(
    token: str,
    feedback: FeedbackOption,
    new_recommendation: AdvisorRecommendation,
    updated_preferences: GoalPreferences,
) -> None:
    """Update an existing session after a feedback refinement."""
    session = _advisor_sessions.get(token)
    if session:
        session.feedback_history.append(feedback)
        session.last_recommendation = new_recommendation
        session.preferences = updated_preferences
        session.last_active = datetime.utcnow()


# ---------------------------------------------------------------------------
# Feedback → preference adjustments
# ---------------------------------------------------------------------------

# Human-readable labels for the refine prompt
FEEDBACK_LABELS: dict[FeedbackOption, str] = {
    FeedbackOption.good_recommendation: "Good recommendation",
    FeedbackOption.too_expensive: "Too expensive",
    FeedbackOption.too_risky: "Too risky",
    FeedbackOption.wrong_location: "Wrong location",
    FeedbackOption.need_more_acreage: "Need more acreage",
    FeedbackOption.need_utilities: "Need utilities",
    FeedbackOption.prefer_lower_price_per_acre: "Prefer lower price per acre",
    FeedbackOption.show_alternatives: "Show alternatives",
}


def apply_feedback_to_preferences(
    preferences: GoalPreferences,
    feedback: FeedbackOption,
) -> GoalPreferences:
    """
    Return a new GoalPreferences object with adjustments applied based on feedback.
    The original preferences object is never mutated.
    """
    updated = deepcopy(preferences)

    if feedback == FeedbackOption.too_expensive:
        if updated.budget_max is not None:
            updated.budget_max = updated.budget_max * 0.80  # Tighten budget by 20%
        # No change if budget wasn't set — AI will deprioritize expensive plots via prompt

    elif feedback == FeedbackOption.too_risky:
        updated.risk_tolerance = "low"

    elif feedback == FeedbackOption.wrong_location:
        # Clear the location so the scorer doesn't penalise all remaining plots
        updated.preferred_location = None

    elif feedback == FeedbackOption.need_more_acreage:
        if updated.min_acres is not None:
            updated.min_acres = updated.min_acres * 1.5
        else:
            updated.min_acres = 2.0  # Default minimum if not previously set

    elif feedback == FeedbackOption.need_utilities:
        # Upgrade preferred utilities to required
        required = set(updated.utilities_required)
        required.update(["water", "electricity"])
        updated.utilities_required = sorted(required)
        updated.utilities_preferred = []

    elif feedback == FeedbackOption.prefer_lower_price_per_acre:
        updated.price_per_acre_priority = True

    # show_alternatives and good_recommendation: no preference change
    # (handled separately in the endpoint logic)

    return updated


def is_no_op_feedback(feedback: FeedbackOption) -> bool:
    """
    Returns True for feedback options that don't require a new AI call
    (show_alternatives just reveals existing data; good_recommendation ends the session).
    """
    return feedback in {
        FeedbackOption.show_alternatives,
        FeedbackOption.good_recommendation,
    }
