from typing import Any, Literal, Protocol
from app.models import Plot
from app.database import SessionLocal
from app.agents.context import ToolContext

def _ranked_plot_ids_from_state(tool_context: ToolContext | None) -> list[int]:
    if not tool_context:
        return []
    ranked_plots = tool_context.state.get("ranked_plots", [])
    return [
        int(plot["id"])
        for plot in ranked_plots
        if isinstance(plot, dict) and plot.get("id") is not None
    ]


def _plots_by_ids(plot_ids: list[int]) -> list[Plot]:
    if not plot_ids:
        return []
    db = SessionLocal()
    try:
        plots = db.query(Plot).filter(Plot.id.in_(plot_ids)).all()
        order = {plot_id: index for index, plot_id in enumerate(plot_ids)}
        return sorted(plots, key=lambda plot: order.get(plot.id, len(order)))
    finally:
        db.close()


def calculate_investment_analysis(
    tool_context: ToolContext | None = None,
) -> dict:
    """Calculates deterministic investment metrics for the current ranked plots."""
    plot_ids = _ranked_plot_ids_from_state(tool_context)
    plots = _plots_by_ids(plot_ids)
    filters = tool_context.state.get("filters", {}) if tool_context else {}
    max_budget = filters.get("max_price") if isinstance(filters, dict) else None

    metrics = [
        calculate_investment_metrics(plot, max_budget=max_budget) for plot in plots
    ]
    if tool_context:
        tool_context.state["investment_metrics"] = metrics
    return {"status": "success", "investment_metrics": metrics}


def calculate_risk_analysis(tool_context: ToolContext | None = None) -> dict:
    """Calculates deterministic risk metrics for the current ranked plots."""
    plots = _plots_by_ids(_ranked_plot_ids_from_state(tool_context))
    metrics = [calculate_risk_metrics(plot) for plot in plots]
    if tool_context:
        tool_context.state["risk_metrics"] = metrics
    return {"status": "success", "risk_metrics": metrics}


def calculate_location_analysis(tool_context: ToolContext | None = None) -> dict:
    """Calculates deterministic location metrics for the current ranked plots."""
    plots = _plots_by_ids(_ranked_plot_ids_from_state(tool_context))
    filters = tool_context.state.get("filters", {}) if tool_context else {}
    purpose = filters.get("purpose") if isinstance(filters, dict) else None
    metrics = [calculate_location_metrics(plot, purpose=purpose) for plot in plots]
    if tool_context:
        tool_context.state["location_metrics"] = metrics
    return {"status": "success", "location_metrics": metrics}


def calculate_catalog_analysis(tool_context: ToolContext | None = None) -> dict:
    """Builds a combined deterministic analysis bundle for ranked plots."""
    plots = _plots_by_ids(_ranked_plot_ids_from_state(tool_context))
    filters = tool_context.state.get("filters", {}) if tool_context else {}
    max_budget = filters.get("max_price") if isinstance(filters, dict) else None
    purpose = filters.get("purpose") if isinstance(filters, dict) else None
    analysis = build_catalog_analysis(
        plots,
        max_budget=max_budget,
        purpose=purpose,
    )
    if tool_context:
        tool_context.state["combined_analysis"] = analysis
    return {"status": "success", "combined_analysis": analysis}

RiskLevel = Literal["Low", "Medium", "High"]


class PlotLike(Protocol):
    id: int
    title: str
    description: str | None
    price: float
    area_acres: float
    city: str
    state: str
    zoning_type: str | None
    road_access: bool
    water_access: bool
    electricity: bool
    sewer: bool
    nearby_landmarks: str | None
    ideal_for: str | None
    risk_notes: str | None
    computed_appreciation: str
    computed_risk_level: str


def _clamp_score(value: float, minimum: int = 0, maximum: int = 10) -> int:
    return max(minimum, min(maximum, round(value)))


def _has_text(value: str | None, *terms: str) -> bool:
    text = (value or "").lower()
    return any(term in text for term in terms)


def _utility_count(plot: PlotLike) -> int:
    return sum(
        1
        for available in [
            plot.road_access,
            plot.water_access,
            plot.electricity,
            plot.sewer,
        ]
        if available
    )


def calculate_price_per_acre(plot: PlotLike) -> float | None:
    if plot.area_acres <= 0:
        return None
    return round(plot.price / plot.area_acres, 2)


def calculate_budget_fit(
    plot: PlotLike, max_budget: float | None = None
) -> dict[str, Any]:
    if max_budget is None or max_budget <= 0:
        return {
            "budget": None,
            "fits_budget": None,
            "budget_fit_score": 7,
            "budget_gap": None,
        }

    budget_gap = round(max_budget - plot.price, 2)
    if budget_gap >= 0:
        score = 10 if plot.price <= max_budget * 0.9 else 8
    else:
        overage_ratio = abs(budget_gap) / max_budget
        score = _clamp_score(7 - overage_ratio * 10)

    return {
        "budget": max_budget,
        "fits_budget": budget_gap >= 0,
        "budget_fit_score": score,
        "budget_gap": budget_gap,
    }


def calculate_utility_score(plot: PlotLike) -> dict[str, Any]:
    available = {
        "road_access": plot.road_access,
        "water_access": plot.water_access,
        "electricity": plot.electricity,
        "sewer": plot.sewer,
    }
    missing = [name for name, value in available.items() if not value]
    score = _clamp_score((_utility_count(plot) / len(available)) * 10)
    return {
        "utility_score": score,
        "available": available,
        "missing": missing,
    }


def calculate_development_readiness(plot: PlotLike) -> dict[str, Any]:
    score = calculate_utility_score(plot)["utility_score"]
    zoning = (plot.zoning_type or "").lower()

    if zoning in {"residential", "commercial"}:
        score += 1
    elif zoning == "agricultural":
        score -= 1

    if _has_text(plot.risk_notes, "restriction", "permit", "flood", "limited"):
        score -= 2

    readiness_score = _clamp_score(score)
    if readiness_score >= 8:
        readiness = "High"
    elif readiness_score >= 5:
        readiness = "Moderate"
    else:
        readiness = "Low"

    return {
        "development_readiness": readiness,
        "development_readiness_score": readiness_score,
    }


def calculate_investment_metrics(
    plot: PlotLike,
    max_budget: float | None = None,
) -> dict[str, Any]:
    utility = calculate_utility_score(plot)
    budget = calculate_budget_fit(plot, max_budget)
    readiness = calculate_development_readiness(plot)
    price_per_acre = calculate_price_per_acre(plot)

    zoning_bonus = (
        2 if (plot.zoning_type or "").lower() in {"commercial", "residential"} else 1
    )
    appreciation_bonus = {"High": 2, "Moderate": 1, "Low": 0}.get(
        plot.computed_appreciation,
        1,
    )
    risk_penalty = {"Low": 0, "Medium": 1, "High": 3}.get(plot.computed_risk_level, 1)

    score = (
        budget["budget_fit_score"] * 0.25
        + utility["utility_score"] * 0.25
        + readiness["development_readiness_score"] * 0.25
        + (6 + zoning_bonus + appreciation_bonus - risk_penalty) * 0.25
    )
    investment_score = _clamp_score(score)

    pros: list[str] = []
    cons: list[str] = []
    if price_per_acre is not None:
        pros.append(f"Price per acre is ${price_per_acre:,.0f}")
    if utility["utility_score"] >= 8:
        pros.append("Most core utilities and access are available")
    if readiness["development_readiness"] == "High":
        pros.append("High development readiness based on utilities and zoning")
    if plot.computed_appreciation == "High":
        pros.append("High appreciation signal based on available plot data")
    if budget["fits_budget"] is False:
        cons.append("Price exceeds the stated budget")
    if utility["missing"]:
        cons.append(f"Missing utilities/access: {', '.join(utility['missing'])}")
    if plot.computed_risk_level == "High":
        cons.append("High risk level requires deeper due diligence")

    return {
        "plot_id": plot.id,
        "price_per_acre": price_per_acre,
        **budget,
        **utility,
        **readiness,
        "investment_score": investment_score,
        "pros": pros[:4],
        "cons": cons[:4],
    }


def calculate_risk_metrics(plot: PlotLike) -> dict[str, Any]:
    notes = (plot.risk_notes or "") + " " + (plot.description or "")
    missing_utilities = calculate_utility_score(plot)["missing"]

    infrastructure_risk = 2
    if not plot.road_access:
        infrastructure_risk += 3
    if not plot.sewer:
        infrastructure_risk += 2
    if _has_text(notes, "flood", "hazard", "limited", "restriction"):
        infrastructure_risk += 2

    utility_risk = len(missing_utilities) * 2
    zoning = (plot.zoning_type or "").lower()
    zoning_risk = 3
    if zoning in {"residential", "commercial"}:
        zoning_risk = 2
    elif zoning in {"agricultural", "industrial"}:
        zoning_risk = 5
    if _has_text(notes, "zoning", "restriction", "hoa", "permit"):
        zoning_risk += 2

    overall_risk_score = _clamp_score(
        infrastructure_risk * 0.4 + utility_risk * 0.35 + zoning_risk * 0.25
    )
    if overall_risk_score >= 7:
        risk_level: RiskLevel = "High"
    elif overall_risk_score >= 4:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    mitigations: list[str] = []
    if not plot.road_access:
        mitigations.append("Verify legal road or easement access before purchase")
    if missing_utilities:
        mitigations.append("Request utility extension estimates for missing services")
    if _has_text(notes, "flood"):
        mitigations.append("Order floodplain and drainage due diligence")
    if _has_text(notes, "restriction", "hoa", "permit", "zoning"):
        mitigations.append(
            "Confirm zoning, HOA, and permitting constraints with local authorities"
        )
    if not mitigations:
        mitigations.append(
            "Confirm title, survey, utilities, and local permitting during due diligence"
        )

    return {
        "plot_id": plot.id,
        "infrastructure_risk": _clamp_score(infrastructure_risk),
        "utility_risk": _clamp_score(utility_risk),
        "zoning_risk": _clamp_score(zoning_risk),
        "overall_risk_score": overall_risk_score,
        "risk_level": risk_level,
        "mitigation_suggestions": mitigations[:4],
    }


def calculate_location_metrics(
    plot: PlotLike,
    purpose: str | None = None,
) -> dict[str, Any]:
    landmarks = [
        item.strip()
        for item in (plot.nearby_landmarks or "").split(",")
        if item.strip()
    ]
    ideal_for = (plot.ideal_for or "").lower()
    purpose_text = (purpose or "").lower()

    nearby_landmark_score = _clamp_score(3 + len(landmarks) * 2)
    accessibility = _clamp_score(
        (6 if plot.road_access else 2) + (2 if plot.city else 0)
    )

    purpose_suitability = 6
    if purpose_text and purpose_text in ideal_for:
        purpose_suitability = 10
    elif purpose_text and any(word in ideal_for for word in purpose_text.split()):
        purpose_suitability = 8
    elif not purpose_text and plot.ideal_for:
        purpose_suitability = 7

    location_score = _clamp_score(
        nearby_landmark_score * 0.35 + accessibility * 0.35 + purpose_suitability * 0.3
    )

    best_use = (
        plot.ideal_for.split(",")[0].strip() if plot.ideal_for else "General land use"
    )

    return {
        "plot_id": plot.id,
        "location_score": location_score,
        "nearby_landmark_score": nearby_landmark_score,
        "accessibility": accessibility,
        "purpose_suitability": purpose_suitability,
        "best_use": best_use,
        "landmarks": landmarks,
    }


def build_plot_analysis(
    plot: PlotLike,
    max_budget: float | None = None,
    purpose: str | None = None,
) -> dict[str, Any]:
    return {
        "plot_id": plot.id,
        "title": plot.title,
        "investment": calculate_investment_metrics(plot, max_budget=max_budget),
        "risk": calculate_risk_metrics(plot),
        "location": calculate_location_metrics(plot, purpose=purpose),
    }


def build_catalog_analysis(
    plots: list[PlotLike],
    max_budget: float | None = None,
    purpose: str | None = None,
) -> list[dict[str, Any]]:
    return [
        build_plot_analysis(plot, max_budget=max_budget, purpose=purpose)
        for plot in plots
    ]