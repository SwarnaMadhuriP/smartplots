"""
Pydantic schemas for the goal-based AI Advisor.
All request/response models for POST /advisor/recommend and POST /advisor/feedback.
"""

from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class GoalKey(str, Enum):
    build_home = "build_home"
    invest_appreciation = "invest_appreciation"
    retirement_lifestyle = "retirement_lifestyle"
    commercial = "commercial"
    maximize_value = "maximize_value"


class FeedbackOption(str, Enum):
    good_recommendation = "good_recommendation"
    too_expensive = "too_expensive"
    too_risky = "too_risky"
    wrong_location = "wrong_location"
    need_more_acreage = "need_more_acreage"
    need_utilities = "need_utilities"
    prefer_lower_price_per_acre = "prefer_lower_price_per_acre"
    show_alternatives = "show_alternatives"


class GoalPreferences(BaseModel):
    """Goal-specific user preferences. Fields not relevant to a goal are None."""

    budget_max: float | None = Field(None, description="Maximum spend in USD")
    preferred_location: str | None = Field(None, description="City, state, or region")
    min_acres: float | None = Field(None, description="Minimum plot size in acres")

    # Utility requirements
    utilities_required: list[str] = Field(
        default_factory=list,
        description="Required utilities: 'water' | 'electricity' | 'sewer'",
    )
    utilities_preferred: list[str] = Field(
        default_factory=list,
        description="Preferred (soft) utilities when not strictly required",
    )

    # Access / zoning
    road_access_required: bool = Field(False)
    zoning_preference: str | None = Field(
        None, description="e.g. 'residential', 'commercial', 'agricultural'"
    )
    commercial_zoning_required: bool | None = Field(None)

    # Risk / investment
    risk_tolerance: str | None = Field(None, description="'low' | 'medium' | 'high'")
    time_horizon: str | None = Field(
        None, description="'1-3 years' | '3-5 years' | '5+ years'"
    )

    # Lifestyle
    quiet_area: bool | None = Field(None)

    # Value prioritization
    price_per_acre_priority: bool | None = Field(None)


class RecommendRequest(BaseModel):
    goal: GoalKey
    preferences: GoalPreferences


class FeedbackRequest(BaseModel):
    session_token: str
    feedback: FeedbackOption


class PlotRecommendationItem(BaseModel):
    plot_id: int
    title: str
    location: str
    price: str               # Formatted: "$120,000"
    acres: str               # Formatted: "2.5 Acres"
    score: float = Field(ge=0, le=10)
    match_reason: str


class AlternativeItem(BaseModel):
    plot_id: int
    title: str
    location: str
    price: str
    acres: str
    key_differentiator: str


class AdvisorRecommendation(BaseModel):
    recommended_plots: list[PlotRecommendationItem]
    primary_recommendation: PlotRecommendationItem
    confidence: float = Field(ge=0.0, le=1.0)
    notices: list[str] = Field(default_factory=list)
    reasoning: list[str]
    risks: list[str]
    tradeoffs: list[str]
    alternatives: list[AlternativeItem]
    next_steps: list[str]
    session_token: str
