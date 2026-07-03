"""
SmartPlots AI Advisor — ADK 2.0-Style Graph Workflow
=====================================================

This module implements a graph-style workflow for the AI Advisor, inspired by
the Google/Kaggle "ambient expense-agent" codelab pattern.

HOW IT MAPS TO ADK 2.0 GRAPH CONCEPTS
--------------------------------------
In ADK 2.0, a WorkflowAgent defines a directed graph where:
  - Each Node is a discrete processing step
  - State flows from node to node via a shared context object
  - Conditional Edges implement branching (routing)
  - Tool calls are nodes that invoke LLMs or external APIs

This file mirrors that structure in plain Python:

  ADK 2.0 Concept              | This File
  -----------------------------|------------------------------------------
  WorkflowAgent / Graph        | AdvisorWorkflow (orchestrator class)
  Node                         | Each *_node(state) function
  State / Context              | WorkflowState dataclass
  Conditional Edge / Router    | decision_router_node() return value
  Tool call (LLM)              | fast_recommendation_node / specialist_review_node
  HITL approval step           | Existing /advisor/feedback loop (FeedbackOption enum)
  Session                      | AdvisorSession in feedback_mapper.py (unchanged)GRAPH TOPOLOGY
--------------

  [input_guard_node]
         ↓
  [preference_context_node]
         ↓
  [deterministic_scoring_node]          ← Pure Python, NO Gemini call
         ↓
  [decision_router_node]                ← Pure Python routing logic
         ↙                      ↘
  [fast_recommendation_node]   ┌─────────────────────────────────────┐
                               │   SPECIALIST PANEL (multi-agent)    │
                               │                                     │
                               │   [investment_analysis_node]        │
                               │   [risk_analysis_node]              │  ← ParallelAgent equivalent
                               │   [location_analysis_node]          │
                               │   [document_intelligence_node]      │
                               │                                     │
                               │   [specialist_review_node]          │  ← Gemini synthesis
                               └─────────────────────────────────────┘
         ↘                      ↙
    [recommendation_composer_node]   ← Normalise + validate AI output

MULTI-AGENT SPECIALIST PANEL
------------------------------
When the router selects specialist_review, the workflow chooses a goal-aware
subset from the 4-node specialist panel before making the Gemini call:

  investment_analysis_node   → calls calculate_investment_metrics() directly
  risk_analysis_node         → calls calculate_risk_metrics() directly
  location_analysis_node     → calls calculate_location_metrics() directly
  document_intelligence_node → calls retrieve_plot_documents() (RAG) if docs exist

This mirrors the ADK orchestrator's ParallelAgent("analysts", [...]) pattern
in app/agents/orchestrator.py. The underlying tool functions are identical.
Instead of running full ADK Agent objects (which require session runners),
we call their deterministic tool functions directly — the same functions
the ADK agents call via their tools — and collect outputs into WorkflowState.

The specialist_review_node then builds an enriched Gemini prompt containing
the executed specialist reports, mirroring what recommendation_agent does in
the ADK SmartPlots orchestrator.

ADK 2.0 MAPPING (full table)
------------------------------
  ADK 2.0 Concept                         | This File
  ----------------------------------------|----------------------------------------------
  WorkflowAgent / Graph                   | AdvisorWorkflow (orchestrator class)
  Node                                    | Each *_node(state) function
  State / InvocationContext               | WorkflowState dataclass
  ConditionalEdge / Router                | decision_router_node()
  ParallelAgent("analysts", [...])        | run_specialist_panel(state)
  investment_agent → calculate_investment | investment_analysis_node()
  risk_agent → calculate_risk             | risk_analysis_node()
  location_agent → calculate_location    | location_analysis_node()
  document_intelligence_agent → retrieve  | document_intelligence_node()
  recommendation_agent (synthesiser)      | specialist_review_node() Gemini call
  Fast LLM Tool Node                      | fast_recommendation_node()
  OutputComposer                          | recommendation_composer_node()
  HITL approval                           | /advisor/feedback loop (FeedbackOption)
  HITL re-entry                           | run_advisor_feedback_workflow()
  Session                                 | AdvisorSession in feedback_mapper.py

ROUTING RULES (decision_router_node)
--------------------------------------
fast_recommendation  if:  top_score >= 8.5
                          AND score_gap >= 1.0
                          AND no critical preflight notices

specialist_review    if:  top_score < 8.5
                          OR score_gap < 1.0
                          OR critical notices exist
                          OR top plot is missing required utilities
                          OR goal is complex (commercial / invest_appreciation)

HUMAN-IN-THE-LOOP EQUIVALENT
-------------------------------
ADK 2.0 supports a blocking HITL approval step. Here we model it as the
existing feedback refinement loop:
  - User receives a recommendation
  - User sends feedback: too_expensive | too_risky | wrong_location |
                         need_more_acreage | need_utilities | show_alternatives
  - run_advisor_feedback_workflow() re-runs the full graph with adjusted
    preferences, always routing through specialist_review for reconsideration.

This is semantically equivalent to a HITL node that re-enters the graph on
user correction, without requiring a blocking server-side approval.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import cast

from google.genai import types

from app.advisor.prompt_builder import build_recommend_prompt, build_refine_prompt
from app.advisor.schemas import GoalKey, GoalPreferences
from app.advisor.scorer import get_top_plots
from app.core.gemini import call_with_retry
from app.database import SessionLocal
from app.models import Plot
from app.rag.retrieval import retrieve_plot_context
from app.services.advisor_service import advisor_preflight_notices
from app.tools.analysis_tools import (
    calculate_investment_metrics,
    calculate_risk_metrics,
    calculate_location_metrics,
)
from app.tools.document_tools import retrieve_plot_documents

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Routing thresholds — these control the fast vs specialist decision
FAST_PATH_MIN_TOP_SCORE: float = 8.5
FAST_PATH_MIN_SCORE_GAP: float = 1.0

# Goals treated as inherently complex → always use specialist review
COMPLEX_GOALS: frozenset[GoalKey] = frozenset(
    {GoalKey.commercial, GoalKey.invest_appreciation}
)

# Gemini model — kept as gemini-2.5-flash per project config
GEMINI_MODEL = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# Specialist Keys — canonical string identifiers for each specialist node.
# These are used in the routing table and selected_specialists list so the
# panel can dispatch dynamically without if/elif chains.
# ---------------------------------------------------------------------------

SPECIALIST_INVESTMENT = "investment"
SPECIALIST_RISK = "risk"
SPECIALIST_LOCATION = "location"
SPECIALIST_DOCUMENT = "document_intelligence"

# ---------------------------------------------------------------------------
# GOAL-TO-SPECIALIST ROUTING TABLE
# ---------------------------------------------------------------------------
#
# Maps each GoalKey to the baseline set of specialist nodes to run.
# Override rules (applied later in _select_specialists) can add more.
#
# Rationale per goal:
#
#   build_home
#     → RISK      : Structural, utility, and zoning risk matter most for a
#                   home buyer — bad infrastructure is a dealbreaker.
#     → LOCATION  : School districts, accessibility, and neighbourhood fit
#                   are primary concerns for residential buyers.
#     → DOCUMENT  : HOA rules, deed restrictions, flood maps, county permits
#                   are critical to review before building a home.
#     (no INVESTMENT — buyer is not optimising for financial return)
#
#   invest_appreciation
#     → INVESTMENT: Core to this goal — price/acre, development readiness,
#                   ROI signals, and budget fit are the primary lenses.
#     → RISK      : Appreciation requires holding the asset long-term;
#                   infrastructure and zoning risk affect future value.
#     → LOCATION  : Location quality (landmark proximity, accessibility)
#                   is the strongest predictor of appreciation.
#     (no DOCUMENT — investor cares about metrics, not deed details)
#
#   retirement_lifestyle
#     → LOCATION  : Primary driver — tranquillity, proximity to amenities,
#                   accessibility for ageing residents.
#     → RISK      : Flood risk, utility reliability, and HOA constraints
#                   affect long-term livability.
#     → DOCUMENT  : HOA rules, utility reports, and zoning restrictions
#                   directly impact lifestyle quality.
#     (no INVESTMENT — retiree optimises for lifestyle, not financial return)
#
#   commercial
#     → INVESTMENT: Commercial buyers need price/acre, development readiness,
#                   and ROI metrics to justify the purchase.
#     → LOCATION  : Accessibility, road access, and proximity to traffic
#                   generators are critical for commercial viability.
#     → DOCUMENT  : Zoning permits, county records, and HOA restrictions
#                   directly block or enable commercial development.
#     (no RISK — commercial due diligence is captured via INVESTMENT + DOCUMENT)
#
#   maximize_value
#     → INVESTMENT: Pure value optimisation — investment score, price/acre,
#                   development readiness, and budget fit are the full story.
#     → RISK      : Risk-adjusted return requires understanding what risks
#                   will suppress value or require mitigation costs.
#     (no LOCATION, no DOCUMENT — maximising value is a financial lens)
#
# ---------------------------------------------------------------------------

SPECIALIST_ROUTING_TABLE: dict[GoalKey, list[str]] = {
    GoalKey.build_home: [
        SPECIALIST_RISK,
        SPECIALIST_LOCATION,
        SPECIALIST_DOCUMENT,
    ],
    GoalKey.invest_appreciation: [
        SPECIALIST_INVESTMENT,
        SPECIALIST_RISK,
        SPECIALIST_LOCATION,
    ],
    GoalKey.retirement_lifestyle: [
        SPECIALIST_LOCATION,
        SPECIALIST_RISK,
        SPECIALIST_DOCUMENT,
    ],
    GoalKey.commercial: [
        SPECIALIST_INVESTMENT,
        SPECIALIST_LOCATION,
        SPECIALIST_DOCUMENT,
    ],
    GoalKey.maximize_value: [
        SPECIALIST_INVESTMENT,
        SPECIALIST_RISK,
    ],
}

# ---------------------------------------------------------------------------
# WorkflowState — the shared context object threaded through all nodes
# (Equivalent to ADK 2.0 State / InvocationContext)
# ---------------------------------------------------------------------------


@dataclass
class SpecialistAnalysis:
    """
    Holds the outputs of the 4 specialist analysis nodes.

    ADK 2.0 mapping: Equivalent to the shared session state keys written by
    each specialist agent via output_key:
      investment_agent  → output_key="investment_analysis"  → investment
      risk_agent        → output_key="risk_analysis"         → risk
      location_agent    → output_key="location_analysis"     → location
      document_agent    → output_key="document_analysis"     → documents
    """
    investment: dict | None = None       # from calculate_investment_metrics()
    risk: dict | None = None             # from calculate_risk_metrics()
    location: dict | None = None         # from calculate_location_metrics()
    documents: list[dict] = field(default_factory=list)  # from retrieve_plot_documents()


@dataclass
class WorkflowState:
    """
    Shared state object passed between every graph node.

    This is the ADK 2.0 equivalent of the agent's InvocationContext / State.
    Each node reads from and writes to this object. No node directly calls
    another node — the orchestrator (AdvisorWorkflow.run) handles sequencing.
    """

    # ── Inputs (set at workflow entry) ──────────────────────────────────────
    goal: GoalKey
    preferences: GoalPreferences
    plots: list[Plot]

    # Optional: set only during feedback refinement passes
    feedback_label: str | None = None

    # ── Populated by preference_context_node ────────────────────────────────
    notices: list[str] = field(default_factory=list)
    budget_tight: bool = False           # True if budget < 25th percentile of catalog
    complex_goal: bool = False           # True for commercial / invest_appreciation

    # ── Populated by deterministic_scoring_node ──────────────────────────────
    top_plots: list[tuple[Plot, float]] = field(default_factory=list)
    top_score: float = 0.0
    score_gap: float = 0.0              # Score difference between rank-1 and rank-2

    # ── Populated by rag_retrieval_node ──────────────────────────────────────
    rag_context: list[dict] = field(default_factory=list)
    rag_unavailable_reason: str | None = None

    # ── Populated by decision_router_node ────────────────────────────────────
    route_taken: str = ""               # "fast_recommendation" | "specialist_review"
    reason_for_route: str = ""
    # Ordered list of specialist keys to run (set by _select_specialists).
    # Empty on the fast path — only populated when route_taken == "specialist_review".
    # Values are the SPECIALIST_* constants: "investment", "risk", "location",
    # "document_intelligence". The panel executes exactly these nodes in order.
    selected_specialists: list[str] = field(default_factory=list)

    # ── Populated by run_specialist_panel (specialist path only) ─────────────
    specialist_analysis: SpecialistAnalysis | None = None

    # ── Populated by fast/specialist nodes, consumed by composer ─────────────
    ai_result: dict | None = None       # Raw dict from Gemini (GoalRecommendationOutput)


# ---------------------------------------------------------------------------
# NODE 1 — Input Guard
# (ADK 2.0 equivalent: InputGuard / pre-condition node)
# ---------------------------------------------------------------------------


def input_guard_node(state: WorkflowState) -> WorkflowState:
    """
    Validate that the workflow has the minimum required inputs.

    ADK 2.0 mapping: This is an InputGuard node — it fires before any
    processing and raises immediately on bad input, preventing unnecessary
    LLM calls or scorer work on invalid requests.
    """
    if not state.plots:
        raise ValueError("Advisor workflow requires at least one plot in the catalog.")
    if state.goal not in GoalKey.__members__.values():
        raise ValueError(f"Unknown goal: {state.goal!r}")
    logger.debug("[AdvisorWorkflow] input_guard_node ✓ — %d plots in catalog", len(state.plots))
    return state


# ---------------------------------------------------------------------------
# NODE 2 — Preference Context Builder
# (ADK 2.0 equivalent: ContextBuilder / enrichment node)
# ---------------------------------------------------------------------------


def preference_context_node(state: WorkflowState) -> WorkflowState:
    """
    Run preflight checks and enrich state with context flags.

    ADK 2.0 mapping: This is a context enrichment node. It does not call the
    LLM — it gathers context that will influence routing and the Gemini prompt.
    In ADK graph terms, it's a pure Python tool node.

    Sets on state:
      - notices: list of user-visible preflight warnings
      - budget_tight: True when budget is very constrained vs catalog
      - complex_goal: True for goals requiring deeper specialist analysis
    """
    state.notices = advisor_preflight_notices(state.plots, state.goal, state.preferences)

    # Detect budget-tight condition: budget is set and < 25th percentile of catalog prices
    if state.preferences.budget_max is not None:
        prices = sorted(cast(float, p.price) for p in state.plots)
        p25: float = prices[max(0, len(prices) // 4)]
        state.budget_tight = state.preferences.budget_max < p25

    # Flag complex goals that warrant specialist review regardless of score
    state.complex_goal = state.goal in COMPLEX_GOALS

    logger.debug(
        "[AdvisorWorkflow] preference_context_node — notices=%d, budget_tight=%s, complex_goal=%s",
        len(state.notices),
        state.budget_tight,
        state.complex_goal,
    )
    return state


# ---------------------------------------------------------------------------
# NODE 3 — Deterministic Scorer
# (ADK 2.0 equivalent: DeterministicTool / Python tool node)
# ---------------------------------------------------------------------------


def deterministic_scoring_node(state: WorkflowState) -> WorkflowState:
    """
    Run the pure-Python scorer against the full plot catalog.

    ADK 2.0 mapping: This is a deterministic tool node — it calls a Python
    function (not an LLM) and writes structured results to state. The scorer
    hard-filters disqualifying plots and ranks the rest 0–10.

    KEY DESIGN PRINCIPLE: Gemini is NOT called here. All scoring happens in
    Python. The LLM only receives the pre-scored shortlist, never the raw catalog.

    Sets on state:
      - top_plots: ranked list of (Plot, score) tuples
      - top_score: score of the #1 ranked plot
      - score_gap: score difference between rank-1 and rank-2 plots
    """
    state.top_plots = get_top_plots(state.plots, state.goal, state.preferences)

    if not state.top_plots:
        raise ValueError(
            "No plots match your criteria after scoring. "
            "Try relaxing your budget, location, or utility requirements."
        )

    state.top_score = state.top_plots[0][1]
    state.score_gap = (
        state.top_plots[0][1] - state.top_plots[1][1]
        if len(state.top_plots) > 1
        else state.top_score  # Only one plot — gap is the score itself
    )

    logger.debug(
        "[AdvisorWorkflow] deterministic_scoring_node — top_score=%.2f, score_gap=%.2f, qualified_plots=%d",
        state.top_score,
        state.score_gap,
        len(state.top_plots),
    )
    return state


# ---------------------------------------------------------------------------
# NODE 4 — RAG Retrieval
# ---------------------------------------------------------------------------


def build_rag_query(state: WorkflowState) -> str:
    """Build a retrieval query from the user's goal and concrete preferences."""
    prefs = state.preferences
    query_parts = [
        f"Goal: {state.goal.value}",
        "Find document evidence about zoning, utilities, access, risks, restrictions, due diligence, and suitability.",
    ]
    if prefs.preferred_location:
        query_parts.append(f"Preferred location: {prefs.preferred_location}")
    if prefs.utilities_required:
        query_parts.append(f"Required utilities: {', '.join(prefs.utilities_required)}")
    if prefs.utilities_preferred:
        query_parts.append(f"Preferred utilities: {', '.join(prefs.utilities_preferred)}")
    if prefs.zoning_preference:
        query_parts.append(f"Zoning preference: {prefs.zoning_preference}")
    if prefs.commercial_zoning_required:
        query_parts.append("Commercial zoning is required.")
    if prefs.road_access_required:
        query_parts.append("Road access, frontage, driveway access, or easements are required.")
    if prefs.quiet_area is not None:
        query_parts.append(f"Quiet or rural area preferred: {prefs.quiet_area}")
    if prefs.risk_tolerance:
        query_parts.append(f"Risk tolerance: {prefs.risk_tolerance}")
    if prefs.time_horizon:
        query_parts.append(f"Time horizon: {prefs.time_horizon}")
    return " ".join(query_parts)


def rag_prompt_chunks(state: WorkflowState) -> list[str]:
    """
    Convert retrieved RAG rows into compact prompt evidence with citations.

    The LLM sees this as supporting evidence only; deterministic plot scores
    remain authoritative and are re-applied after the model responds.
    """
    if not state.rag_context:
        reason = state.rag_unavailable_reason or (
            "No uploaded document evidence was retrieved for the shortlisted plots."
        )
        return [f"Document evidence unavailable: {reason}"]

    chunks: list[str] = []
    for item in state.rag_context:
        page = item.get("page_number")
        page_text = f", page {page}" if page else ""
        text = str(item.get("text", "")).strip()
        if len(text) > 700:
            text = text[:700].rstrip() + "..."
        chunks.append(
            "Plot #{plot_id} [{document_type} — {filename}{page_text}]: {text}".format(
                plot_id=item.get("plot_id", "unknown"),
                document_type=item.get("document_type", "document"),
                filename=item.get("filename", "unknown"),
                page_text=page_text,
                text=text or "No extractable text.",
            )
        )
    return chunks


def rag_retrieval_node(state: WorkflowState) -> WorkflowState:
    """
    Retrieve document evidence for the deterministic shortlist.

    This node intentionally runs after deterministic scoring and before any AI
    recommendation call. It never changes scores, rankings, routing, or API
    response models; it only adds cited document context for the explanation.
    """
    plot_ids = [cast(int, plot.id) for plot, _score in state.top_plots]
    query = build_rag_query(state)

    db = SessionLocal()
    try:
        state.rag_context = retrieve_plot_context(
            plot_ids=plot_ids,
            query=query,
            db=db,
            limit_per_plot=3,
        )
        if not state.rag_context:
            state.rag_unavailable_reason = (
                "No uploaded document evidence was found for the shortlisted plots."
            )
        logger.info(
            "[AdvisorWorkflow] rag_retrieval_node — retrieved %d chunk(s) for %d shortlisted plot(s)",
            len(state.rag_context),
            len(plot_ids),
        )
    except Exception as exc:  # noqa: BLE001
        state.rag_context = []
        state.rag_unavailable_reason = "Document evidence was unavailable for this run."
        logger.warning("[AdvisorWorkflow] rag_retrieval_node failed: %s", exc)
    finally:
        db.close()

    return state


# ---------------------------------------------------------------------------
# NODE 5 — Decision Router
# (ADK 2.0 equivalent: ConditionalEdge / router node)
# ---------------------------------------------------------------------------


def decision_router_node(state: WorkflowState) -> WorkflowState:
    """
    Decide whether to use the fast or specialist recommendation path.

    ADK 2.0 mapping: This is the conditional edge / routing node in the graph.
    In ADK 2.0, a router node returns a route key that the graph executor uses
    to select the next node. Here, we set state.route_taken and state.reason_for_route
    and the orchestrator reads them to branch.

    ROUTING RULES
    ─────────────
    fast_recommendation  →  all conditions met:
      • top_score >= 8.5      (clear winner)
      • score_gap >= 1.0      (not too close to second-best)
      • no critical notices   (no hard preflight failures)

    specialist_review    →  any condition met:
      • top_score < 8.5       (borderline match)
      • score_gap < 1.0       (plots are close, needs nuance)
      • critical notices      (budget, location, utility warnings)
      • complex goal          (commercial / invest_appreciation)
      • feedback refinement   (always re-evaluate on user correction)
    """
    reasons: list[str] = []
    use_specialist = False

    # Always use specialist for feedback refinement passes
    if state.feedback_label is not None:
        use_specialist = True
        reasons.append(f"feedback refinement ({state.feedback_label!r})")

    # Score threshold check
    if state.top_score < FAST_PATH_MIN_TOP_SCORE:
        use_specialist = True
        reasons.append(f"top_score {state.top_score:.2f} < {FAST_PATH_MIN_TOP_SCORE}")

    # Score gap check
    if state.score_gap < FAST_PATH_MIN_SCORE_GAP:
        use_specialist = True
        reasons.append(f"score_gap {state.score_gap:.2f} < {FAST_PATH_MIN_SCORE_GAP}")

    # Preflight notices (any notice counts as critical for routing)
    if state.notices:
        use_specialist = True
        reasons.append(f"{len(state.notices)} preflight notice(s)")

    # Complex goal check
    if state.complex_goal:
        use_specialist = True
        reasons.append(f"complex goal ({state.goal.value})")

    # Missing required utilities on the top plot
    top_plot = state.top_plots[0][0]
    utility_map = {
        "water": top_plot.water_access,
        "electricity": top_plot.electricity,
        "sewer": top_plot.sewer,
    }
    missing_required = [
        u for u in state.preferences.utilities_required
        if not utility_map.get(u, False)
    ]
    if missing_required:
        use_specialist = True
        reasons.append(f"top plot missing required utilities: {missing_required}")

    if use_specialist:
        state.route_taken = "specialist_review"
        state.reason_for_route = "; ".join(reasons) if reasons else "default specialist"
        # ── Select which specialist nodes to run (goal-aware) ─────────────────
        state.selected_specialists = _select_specialists(state, top_plot, missing_required)
    else:
        state.route_taken = "fast_recommendation"
        state.reason_for_route = (
            f"Score {state.top_score:.2f} >= {FAST_PATH_MIN_TOP_SCORE}, "
            f"gap {state.score_gap:.2f} >= {FAST_PATH_MIN_SCORE_GAP}, "
            f"no critical notices"
        )

    # ── Debug log (never sent to frontend) ──────────────────────────────────
    logger.info(
        "[AdvisorWorkflow] route=%s top_score=%.2f score_gap=%.2f specialists=%s reason=%r",
        state.route_taken,
        state.top_score,
        state.score_gap,
        state.selected_specialists or "(fast path)",
        state.reason_for_route,
    )

    return state


# ---------------------------------------------------------------------------
# SPECIALIST SELECTOR — goal-aware routing table + override rules
# Called by decision_router_node immediately after the fast/specialist branch
# decision. Returns the ordered list of specialist keys to execute.
# ---------------------------------------------------------------------------


def _select_specialists(
    state: WorkflowState,
    top_plot: Plot,
    missing_required: list[str],
) -> list[str]:
    """
    Determine which specialist nodes to run based on the goal and overrides.

    Step 1 — Goal baseline
    ──────────────────────
    Look up SPECIALIST_ROUTING_TABLE[goal] to get the default specialist set.
    Each goal maps to the 2–3 most relevant lenses (see table comments).

    Step 2 — Override rules
    ────────────────────────
    Override rules inspect WorkflowState conditions and add specialists that
    the goal baseline may have omitted. Overrides never REMOVE specialists —
    they only ADD. The final set is the union of baseline + overrides.

    Override rules:
      • Missing required utilities  → add RISK + DOCUMENT_INTELLIGENCE
        Rationale: utilities absence is both a risk factor and a legal/doc issue.

      • Close top scores (gap < 1.0) → add INVESTMENT
        Rationale: when plots are neck-and-neck, financial metrics break the tie.

      • Location mismatch notice    → add LOCATION
        Rationale: if preflight detected a location mismatch, the location lens
        must run to explain the tradeoff in the recommendation.

      • Zoning uncertainty          → add DOCUMENT_INTELLIGENCE
        Rationale: missing, unknown, mismatched, or notice-driven zoning issues
        require document-level evidence (county records, permits) to advise
        correctly.

      • High risk level on top plot → add RISK
        Rationale: plot.computed_risk_level == "High" means risk analysis must
        surface mitigation strategies regardless of goal.

    Returns:
        Ordered list of specialist keys preserving: investment → risk →
        location → document_intelligence (consistent prompt section order).
    """
    # ── Step 1: Goal baseline from routing table ───────────────────────────────
    baseline: set[str] = set(
        SPECIALIST_ROUTING_TABLE.get(state.goal, [
            # Fallback: run all 4 if goal is unknown (defensive)
            SPECIALIST_INVESTMENT, SPECIALIST_RISK,
            SPECIALIST_LOCATION, SPECIALIST_DOCUMENT,
        ])
    )
    override_reasons: list[str] = []

    # ── Step 2: Override rules ─────────────────────────────────────────────────

    # Override A: Missing required utilities
    # → add RISK (infrastructure risk is directly elevated)
    # → add DOCUMENT (utility reports/permits needed to resolve)
    if missing_required:
        if SPECIALIST_RISK not in baseline:
            baseline.add(SPECIALIST_RISK)
            override_reasons.append(f"missing utilities {missing_required} → +risk")
        if SPECIALIST_DOCUMENT not in baseline:
            baseline.add(SPECIALIST_DOCUMENT)
            override_reasons.append(f"missing utilities {missing_required} → +document_intelligence")

    # Override B: Close top scores (score_gap < threshold)
    # → add INVESTMENT to break the tie with financial metrics
    if state.score_gap < FAST_PATH_MIN_SCORE_GAP and SPECIALIST_INVESTMENT not in baseline:
        baseline.add(SPECIALIST_INVESTMENT)
        override_reasons.append(f"score_gap {state.score_gap:.2f} is tight → +investment")

    # Override C: Location mismatch in preflight notices
    # → add LOCATION so the recommendation can explain the tradeoff
    location_mismatch = any(
        "location" in n.lower() or "city" in n.lower() or "state" in n.lower()
        for n in state.notices
    )
    if location_mismatch and SPECIALIST_LOCATION not in baseline:
        baseline.add(SPECIALIST_LOCATION)
        override_reasons.append("location mismatch notice → +location")

    # Override D: Zoning uncertainty
    # → add DOCUMENT_INTELLIGENCE (zoning docs / county records needed)
    zoning_notice = any(
        "zoning" in n.lower() or "permit" in n.lower() or "hoa" in n.lower()
        for n in state.notices
    )
    zoning_value = (top_plot.zoning_type or "").strip().lower()
    zoning_unknown = zoning_value in {"", "unknown", "general", "n/a", "none"}
    zoning_preference_mismatch = (
        state.preferences.zoning_preference is not None
        and state.preferences.zoning_preference.strip().lower() not in zoning_value
    )
    commercial_zoning_missing = (
        bool(state.preferences.commercial_zoning_required)
        and "commercial" not in zoning_value
    )
    zoning_uncertainty = (
        zoning_notice
        or zoning_unknown
        or zoning_preference_mismatch
        or commercial_zoning_missing
    )
    if zoning_uncertainty and SPECIALIST_DOCUMENT not in baseline:
        baseline.add(SPECIALIST_DOCUMENT)
        override_reasons.append("zoning uncertainty → +document_intelligence")

    # Override E: High risk level on the top plot
    # → add RISK so mitigation strategies are always surfaced for risky plots
    if str(getattr(top_plot, "computed_risk_level", "")).lower() == "high" and SPECIALIST_RISK not in baseline:
        baseline.add(SPECIALIST_RISK)
        override_reasons.append("top plot computed_risk_level=high → +risk")

    if override_reasons:
        logger.info(
            "[SpecialistSelector] goal=%s overrides applied: %s",
            state.goal.value,
            "; ".join(override_reasons),
        )

    # ── Return ordered list (canonical order: investment → risk → location → doc) ─
    _ORDER = [SPECIALIST_INVESTMENT, SPECIALIST_RISK, SPECIALIST_LOCATION, SPECIALIST_DOCUMENT]
    selected = [s for s in _ORDER if s in baseline]

    logger.info(
        "[SpecialistSelector] goal=%s → specialists=%s",
        state.goal.value,
        selected,
    )
    return selected


# ---------------------------------------------------------------------------
# NODE 6a — Fast Recommendation
# (ADK 2.0 equivalent: FastPath tool node / LLM call with standard prompt)
# ---------------------------------------------------------------------------


def fast_recommendation_node(state: WorkflowState) -> WorkflowState:
    """
    Generate a recommendation via Gemini using the standard prompt.

    ADK 2.0 mapping: This is the 'fast path' LLM tool node. It receives the
    pre-scored shortlist and asks Gemini to produce structured narrative
    explanation only — no additional analysis layers needed.

    Used when: top plot clearly wins (high score, clear gap, no warnings).
    """
    logger.info("[AdvisorWorkflow] fast_recommendation_node — calling Gemini")

    prompt = build_recommend_prompt(
        state.goal,
        state.preferences,
        state.top_plots,
        rag_chunks=rag_prompt_chunks(state),
    )

    response = call_with_retry(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_GoalRecommendationSchema,
            temperature=0.2,
        ),
    )

    if not response.text:
        raise RuntimeError("Fast recommendation: Gemini returned empty response.")

    state.ai_result = _apply_system_scores_to_result(
        json.loads(response.text),
        state.top_plots,
    )
    return state


# ---------------------------------------------------------------------------
# SPECIALIST PANEL — 4 Specialist Nodes + Panel Orchestrator
#
# ADK 2.0 equivalent: ParallelAgent("analysts", [investment_agent,
#                                                  risk_agent,
#                                                  location_agent,
#                                                  document_intelligence_agent])
#
# These nodes call the SAME deterministic tool functions that the ADK specialist
# agents call via their tools[] lists. We call them directly here to avoid
# requiring a full ADK InMemorySessionService + Runner for a synchronous
# FastAPI endpoint. The outputs are written to WorkflowState.specialist_analysis,
# mirroring each agent's output_key= assignment in specialists.py.
# ---------------------------------------------------------------------------


def _goal_to_purpose(goal: GoalKey) -> str:
    """
    Map an advisor GoalKey to a human-readable purpose string for the
    location_agent's purpose parameter (matches ideal_for text in plots).
    """
    mapping = {
        GoalKey.build_home: "residential home",
        GoalKey.invest_appreciation: "investment",
        GoalKey.retirement_lifestyle: "retirement",
        GoalKey.commercial: "commercial",
        GoalKey.maximize_value: "investment",
    }
    return mapping.get(goal, "")


# ---------------------------------------------------------------------------
# SPECIALIST NODE A — Investment Analysis
# ADK equivalent: investment_agent → calculate_investment_analysis tool
# output_key: "investment_analysis" → state.specialist_analysis.investment
# ---------------------------------------------------------------------------


def investment_analysis_node(state: WorkflowState) -> WorkflowState:
    """
    Run deterministic investment analysis on the top-ranked plot.

    ADK 2.0 mapping: Mirrors investment_agent calling calculate_investment_analysis().
    The agent's output_key="investment_analysis" maps to state.specialist_analysis.investment.

    Computes:
      - price_per_acre, budget_fit_score, budget_gap
      - utility_score, missing utilities
      - development_readiness (High / Moderate / Low)
      - investment_score (0-10)
      - pros and cons list
    """
    top_plot, _ = state.top_plots[0]
    budget_max = state.preferences.budget_max

    try:
        metrics = calculate_investment_metrics(top_plot, max_budget=budget_max)
        state.specialist_analysis.investment = metrics  # type: ignore[union-attr]
        logger.info(
            "[SpecialistPanel] investment_analysis_node ✓ — investment_score=%s",
            metrics.get("investment_score", "?"),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("[SpecialistPanel] investment_analysis_node failed: %s", exc)
        state.specialist_analysis.investment = {"error": str(exc)}  # type: ignore[union-attr]

    return state


# ---------------------------------------------------------------------------
# SPECIALIST NODE B — Risk Analysis
# ADK equivalent: risk_agent → calculate_risk_analysis tool
# output_key: "risk_analysis" → state.specialist_analysis.risk
# ---------------------------------------------------------------------------


def risk_analysis_node(state: WorkflowState) -> WorkflowState:
    """
    Run deterministic risk analysis on the top-ranked plot.

    ADK 2.0 mapping: Mirrors risk_agent calling calculate_risk_analysis().
    The agent's output_key="risk_analysis" maps to state.specialist_analysis.risk.

    Computes:
      - infrastructure_risk, utility_risk, zoning_risk (0-10 each)
      - overall_risk_score (0-10)
      - risk_level (Low / Medium / High)
      - mitigation_suggestions list
    """
    top_plot, _ = state.top_plots[0]

    try:
        metrics = calculate_risk_metrics(top_plot)
        state.specialist_analysis.risk = metrics  # type: ignore[union-attr]
        logger.info(
            "[SpecialistPanel] risk_analysis_node ✓ — risk_level=%s, overall_score=%s",
            metrics.get("risk_level", "?"),
            metrics.get("overall_risk_score", "?"),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("[SpecialistPanel] risk_analysis_node failed: %s", exc)
        state.specialist_analysis.risk = {"error": str(exc)}  # type: ignore[union-attr]

    return state


# ---------------------------------------------------------------------------
# SPECIALIST NODE C — Location Analysis
# ADK equivalent: location_agent → calculate_location_analysis tool
# output_key: "location_analysis" → state.specialist_analysis.location
# ---------------------------------------------------------------------------


def location_analysis_node(state: WorkflowState) -> WorkflowState:
    """
    Run deterministic location analysis on the top-ranked plot.

    ADK 2.0 mapping: Mirrors location_agent calling calculate_location_analysis().
    The agent's output_key="location_analysis" maps to state.specialist_analysis.location.

    Computes:
      - location_score (0-10)
      - nearby_landmark_score
      - accessibility
      - purpose_suitability
      - best_use string
      - landmarks list
    """
    top_plot, _ = state.top_plots[0]
    purpose = _goal_to_purpose(state.goal)

    try:
        metrics = calculate_location_metrics(top_plot, purpose=purpose)
        state.specialist_analysis.location = metrics  # type: ignore[union-attr]
        logger.info(
            "[SpecialistPanel] location_analysis_node ✓ — location_score=%s, best_use=%r",
            metrics.get("location_score", "?"),
            metrics.get("best_use", "?"),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("[SpecialistPanel] location_analysis_node failed: %s", exc)
        state.specialist_analysis.location = {"error": str(exc)}  # type: ignore[union-attr]

    return state


# ---------------------------------------------------------------------------
# SPECIALIST NODE D — Document Intelligence
# ADK equivalent: document_intelligence_agent → retrieve_plot_documents tool
# output_key: "document_analysis" → state.specialist_analysis.documents
# ---------------------------------------------------------------------------


def document_intelligence_node(state: WorkflowState) -> WorkflowState:
    """
    Retrieve and surface relevant document chunks for the top-ranked plot.

    ADK 2.0 mapping: Mirrors document_intelligence_agent calling
    retrieve_plot_documents(). The agent's output_key="document_analysis"
    maps to state.specialist_analysis.documents.

    Behaviour:
      - If the top plot has no attached documents → sets documents = [] and logs
      - If documents exist → calls retrieve_plot_documents() with a goal-derived
        question, returns up to 5 most relevant chunks (RAG / cosine similarity)
      - Failures are caught and logged; the specialist prompt still runs
    """
    top_plot, _ = state.top_plots[0]

    # Build the retrieval question from goal context (mirrors document_agent's {query})
    goal_question = (
        f"What are the key investment, zoning, utility, and risk details "
        f"relevant to a {_goal_to_purpose(state.goal)} use for this plot?"
    )

    has_documents = bool(getattr(top_plot, "documents", None))

    if not has_documents:
        logger.info(
            "[SpecialistPanel] document_intelligence_node — no documents attached to plot #%s",
            top_plot.id,
        )
        state.specialist_analysis.documents = []  # type: ignore[union-attr]
        return state

    try:
        chunks = retrieve_plot_documents(plot_id=cast(int, top_plot.id), question=goal_question)
        state.specialist_analysis.documents = chunks  # type: ignore[union-attr]
        logger.info(
            "[SpecialistPanel] document_intelligence_node ✓ — retrieved %d chunk(s) for plot #%s",
            len(chunks),
            top_plot.id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "[SpecialistPanel] document_intelligence_node failed for plot #%s: %s",
            top_plot.id,
            exc,
        )
        state.specialist_analysis.documents = []  # type: ignore[union-attr]

    return state


# ---------------------------------------------------------------------------
# SPECIALIST PANEL ORCHESTRATOR
# ADK equivalent: ParallelAgent("analysts", [investment_agent, risk_agent,
#                                             location_agent, document_agent])
#
# Runs only the selected specialist nodes and collects their outputs into
# WorkflowState. Sequential execution for now (same end result as parallel for
# CPU-bound work). Phase 2 upgrade: wrap selected nodes in
# concurrent.futures.ThreadPoolExecutor for true parallel execution — only
# document_intelligence_node does I/O.
# ---------------------------------------------------------------------------


def run_specialist_panel(state: WorkflowState) -> WorkflowState:
    """
    Orchestrate ONLY the specialist nodes selected by _select_specialists().

    ADK 2.0 mapping: Equivalent to a goal-aware ParallelAgent that decides at
    runtime which sub-agents to activate. Previously ran all 4 unconditionally;
    now dispatches based on state.selected_specialists.

    Execution order is always canonical (investment → risk → location → doc)
    regardless of which subset was selected. This keeps prompt section ordering
    consistent across all goals.
    """
    top_plot_id = state.top_plots[0][0].id
    selected = state.selected_specialists

    logger.info(
        "[SpecialistPanel] Starting goal-aware panel for plot #%s — running: %s",
        top_plot_id,
        selected,
    )

    # Initialise the specialist analysis container (all fields default to None/[])
    state.specialist_analysis = SpecialistAnalysis()

    # ── Dispatch only the selected specialist nodes ────────────────────────────
    # Nodes not in selected_specialists are skipped entirely — their fields in
    # SpecialistAnalysis remain None, and build_specialist_prompt will mark them
    # as "not run for this goal" rather than "unavailable".

    if SPECIALIST_INVESTMENT in selected:
        state = investment_analysis_node(state)       # mirrors investment_agent

    if SPECIALIST_RISK in selected:
        state = risk_analysis_node(state)             # mirrors risk_agent

    if SPECIALIST_LOCATION in selected:
        state = location_analysis_node(state)         # mirrors location_agent

    if SPECIALIST_DOCUMENT in selected:
        state = document_intelligence_node(state)     # mirrors document_intelligence_agent

    logger.info(
        "[SpecialistPanel] Panel complete — %d/%d specialists ran",
        len(selected), 4,
    )
    return state


# ---------------------------------------------------------------------------
# SPECIALIST PROMPT BUILDER
# ADK equivalent: recommendation_agent's synthesis of all specialist outputs
# ---------------------------------------------------------------------------


def build_specialist_prompt(state: WorkflowState) -> str:
    """
    Build an enriched Gemini prompt containing all 4 specialist reports.

    ADK 2.0 mapping: This renders what recommendation_agent receives as
    {investment_analysis}, {risk_analysis}, {location_analysis}, and
    {document_analysis} variables in its instruction template. Gemini then
    acts as the recommendation_agent synthesiser.

    Structure:
      [SPECIALIST PANEL REPORTS]  ← all 4 agent outputs formatted as text
      [Standard recommend/refine prompt]  ← existing prompt_builder output
    """
    sa = state.specialist_analysis
    top_plot, _ = state.top_plots[0]
    sections: list[str] = []

    sections.append("=== SPECIALIST PANEL REPORTS ===")
    sections.append(
        "The following reports were produced by specialist analysis agents "
        "before this prompt was generated. Use them as primary analytical evidence."
    )

    # ── Section 1: Investment Analysis ────────────────────────────────────────
    # Only included if investment_analysis_node ran for this goal.
    sections.append("\n--- 📈 INVESTMENT ANALYSIS (Investment Agent) ---")
    if SPECIALIST_INVESTMENT not in (state.selected_specialists or []):
        sections.append("[Not run for this goal — investment metrics not the primary lens.]")
    elif sa and sa.investment and "error" not in sa.investment:
        inv = sa.investment
        sections.append(f"Investment Score: {inv.get('investment_score', 'N/A')}/10")
        sections.append(f"Price per Acre: ${inv.get('price_per_acre', 0):,.0f}")
        sections.append(f"Budget Fit: {'Yes' if inv.get('fits_budget') else 'No (over budget)' if inv.get('fits_budget') is False else 'N/A'}")
        if inv.get('budget_gap') is not None:
            gap = inv['budget_gap']
            sections.append(f"Budget Gap: {'${:,.0f} under budget'.format(gap) if gap >= 0 else '${:,.0f} over budget'.format(abs(gap))}")
        sections.append(f"Utility Score: {inv.get('utility_score', 'N/A')}/10")
        if inv.get('missing'):
            sections.append(f"Missing Utilities: {', '.join(inv['missing'])}")
        sections.append(f"Development Readiness: {inv.get('development_readiness', 'N/A')} (score: {inv.get('development_readiness_score', 'N/A')}/10)")
        if inv.get('pros'):
            sections.append("Pros: " + " | ".join(inv['pros']))
        if inv.get('cons'):
            sections.append("Cons: " + " | ".join(inv['cons']))
    else:
        sections.append("Investment analysis unavailable.")

    # ── Section 2: Risk Analysis ───────────────────────────────────────────────
    # Only included if risk_analysis_node ran for this goal.
    sections.append("\n--- ⚠️ RISK ANALYSIS (Risk Agent) ---")
    if SPECIALIST_RISK not in (state.selected_specialists or []):
        sections.append("[Not run for this goal — risk is not the primary lens for this goal type.]")
    elif sa and sa.risk and "error" not in sa.risk:
        risk = sa.risk
        sections.append(f"Overall Risk Score: {risk.get('overall_risk_score', 'N/A')}/10 — Risk Level: {risk.get('risk_level', 'N/A')}")
        sections.append(f"Infrastructure Risk: {risk.get('infrastructure_risk', 'N/A')}/10")
        sections.append(f"Utility Risk: {risk.get('utility_risk', 'N/A')}/10")
        sections.append(f"Zoning Risk: {risk.get('zoning_risk', 'N/A')}/10")
        if risk.get('mitigation_suggestions'):
            sections.append("Mitigation Suggestions:")
            for m in risk['mitigation_suggestions']:
                sections.append(f"  • {m}")
    else:
        sections.append("Risk analysis unavailable.")

    # ── Section 3: Location Analysis ──────────────────────────────────────────
    # Only included if location_analysis_node ran for this goal.
    sections.append("\n--- 📍 LOCATION ANALYSIS (Location Agent) ---")
    if SPECIALIST_LOCATION not in (state.selected_specialists or []):
        sections.append("[Not run for this goal — location metrics not the primary lens.]")
    elif sa and sa.location and "error" not in sa.location:
        loc = sa.location
        sections.append(f"Location Score: {loc.get('location_score', 'N/A')}/10")
        sections.append(f"Accessibility: {loc.get('accessibility', 'N/A')}/10")
        sections.append(f"Nearby Landmark Score: {loc.get('nearby_landmark_score', 'N/A')}/10")
        sections.append(f"Purpose Suitability: {loc.get('purpose_suitability', 'N/A')}/10")
        sections.append(f"Best Use: {loc.get('best_use', 'N/A')}")
        if loc.get('landmarks'):
            sections.append(f"Nearby Landmarks: {', '.join(loc['landmarks'])}")
    else:
        sections.append("Location analysis unavailable.")

    # ── Section 4: Document Intelligence ──────────────────────────────────────
    # Only included if document_intelligence_node ran for this goal.
    sections.append("\n--- 📄 DOCUMENT INTELLIGENCE (Document Intelligence Agent) ---")
    if SPECIALIST_DOCUMENT not in (state.selected_specialists or []):
        sections.append("[Not run for this goal — document review not required for this goal type.]")
    elif sa and sa.documents:
        sections.append(f"Retrieved {len(sa.documents)} document chunk(s) for plot #{top_plot.id}:")
        for i, chunk in enumerate(sa.documents, 1):
            doc_type = chunk.get("document_type", "unknown")
            filename = chunk.get("filename", "unknown")
            page = chunk.get("page_number")
            text = chunk.get("text", "")[:400]  # truncate to keep prompt size reasonable
            page_str = f" (page {page})" if page else ""
            sections.append(f"  [{i}] {doc_type} — {filename}{page_str}: {text}")
    else:
        sections.append("No documents are attached to this plot.")
        sections.append("Recommend the user upload zoning docs, surveys, or utility reports for enhanced due diligence.")

    sections.append("\n=== END OF SPECIALIST REPORTS ===")
    sections.append("Use the specialist reports above as grounding evidence in your reasoning, risks, and tradeoffs sections.")

    specialist_block = "\n".join(sections)

    # ── Build the base prompt (feedback-aware) ────────────────────────────────
    rag_chunks = rag_prompt_chunks(state)

    if state.feedback_label:
        base_prompt = build_refine_prompt(
            state.goal,
            state.preferences,
            state.top_plots,
            state.feedback_label,
            rag_chunks=rag_chunks,
        )
    else:
        base_prompt = build_recommend_prompt(
            state.goal,
            state.preferences,
            state.top_plots,
            rag_chunks=rag_chunks,
        )

    # Prepend the specialist panel reports so Gemini synthesises them first
    return specialist_block + "\n\n" + base_prompt


# ---------------------------------------------------------------------------
# NODE 5b — Specialist Review
# (ADK 2.0 equivalent: recommendation_agent synthesis node after ParallelAgent)
# ---------------------------------------------------------------------------


def specialist_review_node(state: WorkflowState) -> WorkflowState:
    """
    Run the goal-aware specialist panel then call Gemini to synthesise findings.

    ADK 2.0 mapping: This node combines:
      1. Goal-aware ParallelAgent  → run_specialist_panel(state)
         Only the specialists selected by _select_specialists() are executed.
         The selection is based on SPECIALIST_ROUTING_TABLE[goal] + override rules.
      2. recommendation_agent      → Gemini call with selected specialist reports

    The Gemini call always happens exactly once, regardless of how many
    specialists ran. build_specialist_prompt() marks unrun sections as
    "[Not run for this goal]" so Gemini knows they were intentionally skipped.

    Used when: scores are close, goals are complex, utilities missing, or
    the user is refining after feedback (HITL re-entry).
    """
    logger.info("[AdvisorWorkflow] specialist_review_node — running specialist panel + Gemini")

    # ── Step 1: Run selected specialist nodes (ADK ParallelAgent equivalent) ──
    state = run_specialist_panel(state)

    # ── Step 2: Build the enriched prompt with all 4 specialist reports ───────
    prompt = build_specialist_prompt(state)

    # ── Step 3: Gemini call — synthesises specialist findings ─────────────────
    # Temperature 0.3: slightly higher than fast path to allow nuanced synthesis
    response = call_with_retry(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_GoalRecommendationSchema,
            temperature=0.3,
        ),
    )

    if not response.text:
        raise RuntimeError("Specialist review: Gemini returned empty response.")

    state.ai_result = _apply_system_scores_to_result(
        json.loads(response.text),
        state.top_plots,
    )
    return state


# ---------------------------------------------------------------------------
# NODE 6 — Recommendation Composer
# (ADK 2.0 equivalent: OutputComposer / response formatting node)
# ---------------------------------------------------------------------------


def recommendation_composer_node(state: WorkflowState) -> WorkflowState:
    """
    Validate and normalise the AI result dict.

    ADK 2.0 mapping: This is the output composer node — it ensures the AI
    response matches the expected schema before it's returned to the API layer.
    It also emits the structured debug log line.

    Adds a small decision_trace field after schema validation so the frontend
    can display the actual route selected by decision_router_node.
    """
    if state.ai_result is None:
        raise RuntimeError("recommendation_composer_node: ai_result is None. Graph routing error.")

    # Validate against the Pydantic schema (same as recommendation_service.py)
    from app.advisor.recommendation_service import GoalRecommendationOutput
    validated = GoalRecommendationOutput.model_validate(state.ai_result)
    state.ai_result = validated.model_dump()
    state.ai_result["decision_trace"] = {
        "route": state.route_taken,
        "selected_specialists": state.selected_specialists,
        "reason_for_route": state.reason_for_route,
        "top_score": state.top_score,
        "score_gap": state.score_gap,
    }

    # ── Structured debug log (never returned to frontend) ────────────────────
    logger.info(
        "[AdvisorWorkflow] COMPLETE route=%s top_score=%.2f score_gap=%.2f reason=%r",
        state.route_taken,
        state.top_score,
        state.score_gap,
        state.reason_for_route,
    )

    return state


# ---------------------------------------------------------------------------
# Schema reference (local import to avoid circular deps)
# ---------------------------------------------------------------------------

# Imported lazily inside nodes to avoid circular imports with recommendation_service
# This mirrors the GoalRecommendationOutput defined in recommendation_service.py
from app.advisor.recommendation_service import (  # noqa: E402
    GoalRecommendationOutput as _GoalRecommendationSchema,
    apply_system_scores_to_result as _apply_system_scores_to_result,
)


# ---------------------------------------------------------------------------
# AdvisorWorkflow — Orchestrator
# (ADK 2.0 equivalent: WorkflowAgent.run() / graph executor)
# ---------------------------------------------------------------------------


class AdvisorWorkflow:
    """
    Orchestrates the advisor graph by sequencing node calls and branching
    on the route returned by decision_router_node.

    ADK 2.0 mapping: This class is the WorkflowAgent / graph executor.
    In ADK 2.0, the graph topology and edge conditions are declared declaratively;
    here we implement the same logic imperatively for clarity and portability.

    GRAPH EXECUTION ORDER
    ─────────────────────
    1. input_guard_node              ← validate inputs
    2. preference_context_node       ← enrich with context flags + notices
    3. deterministic_scoring_node    ← Python scorer (no Gemini)
    4. rag_retrieval_node            ← document evidence for scored shortlist
    5. decision_router_node          ← decide route + select specialists
         calls _select_specialists() → SPECIALIST_ROUTING_TABLE[goal] + overrides
    6a. fast_recommendation_node     (route == "fast_recommendation")
    6b. specialist_review_node       (route == "specialist_review")
         → run_specialist_panel()    ← ONLY selected_specialists run (no Gemini)
         → build_specialist_prompt() ← formats only the reports that ran
         → Gemini call               ← synthesises specialist findings
    6. recommendation_composer_node  ← normalise + validate output
    """

    def run(
        self,
        goal: GoalKey,
        preferences: GoalPreferences,
        plots: list[Plot],
        feedback_label: str | None = None,
    ) -> dict:
        """
        Execute the full advisor graph and return an AdvisorRecommendation-
        compatible dict.

        Args:
            goal: User's selected investment goal.
            preferences: Goal-specific preferences.
            plots: Full plot catalog from DB.
            feedback_label: Human-readable feedback string (e.g. "Too expensive").
                            When set, the workflow is a refinement pass.

        Returns:
            Dict compatible with AdvisorRecommendation schema.

        Raises:
            ValueError: Input validation failures or no qualified plots.
            RuntimeError: Gemini failures propagated from node calls.
        """
        # Initialise shared state — the ADK 2.0 InvocationContext equivalent
        state = WorkflowState(
            goal=goal,
            preferences=preferences,
            plots=plots,
            feedback_label=feedback_label,
        )

        # ── Execute graph nodes in order ─────────────────────────────────────
        state = input_guard_node(state)
        state = preference_context_node(state)
        state = deterministic_scoring_node(state)
        state = rag_retrieval_node(state)
        state = decision_router_node(state)

        # ── Conditional branch (ADK 2.0 conditional edge) ────────────────────
        if state.route_taken == "fast_recommendation":
            state = fast_recommendation_node(state)
        else:
            state = specialist_review_node(state)

        state = recommendation_composer_node(state)
        # ─────────────────────────────────────────────────────────────────────

        return state.ai_result  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Public API — called by recommendation_service.py wrappers
# ---------------------------------------------------------------------------

_workflow = AdvisorWorkflow()


def run_advisor_workflow(
    goal: GoalKey,
    preferences: GoalPreferences,
    plots: list[Plot],
) -> dict:
    """
    Entry point for a fresh recommendation request.
    Called by run_goal_recommendation_via_workflow() in recommendation_service.py.
    """
    return _workflow.run(goal=goal, preferences=preferences, plots=plots)


def run_advisor_feedback_workflow(
    goal: GoalKey,
    preferences: GoalPreferences,
    plots: list[Plot],
    feedback_label: str,
) -> dict:
    """
    Entry point for a feedback-refinement pass.
    Called by run_refine_recommendation_via_workflow() in recommendation_service.py.

    Always routes through specialist_review because the user has indicated
    dissatisfaction — the graph should re-evaluate more carefully.
    This models the ADK 2.0 HITL re-entry pattern.
    """
    return _workflow.run(
        goal=goal,
        preferences=preferences,
        plots=plots,
        feedback_label=feedback_label,
    )
