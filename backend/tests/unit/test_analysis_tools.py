from types import SimpleNamespace

from app.analysis_tools import (
    calculate_investment_metrics,
    calculate_location_metrics,
    calculate_risk_metrics,
)
from app.routers import (
    QuestionRoute,
    SearchRoute,
    classify_question,
    classify_search_query,
)


def make_plot(**overrides):
    defaults = {
        "id": 1,
        "title": "Test Plot",
        "description": "A build-ready residential parcel near downtown.",
        "price": 100_000,
        "area_acres": 2.0,
        "city": "Austin",
        "state": "TX",
        "zoning_type": "residential",
        "road_access": True,
        "water_access": True,
        "electricity": True,
        "sewer": False,
        "nearby_landmarks": "Downtown, Highway 71",
        "ideal_for": "Residential, Investment",
        "risk_notes": "Sewer extension required.",
        "computed_appreciation": "High",
        "computed_risk_level": "Medium",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_investment_metrics_are_deterministic() -> None:
    plot = make_plot()

    metrics = calculate_investment_metrics(plot, max_budget=120_000)

    assert metrics["price_per_acre"] == 50_000
    assert metrics["fits_budget"] is True
    assert metrics["utility_score"] == 8
    assert 0 <= metrics["investment_score"] <= 10
    assert metrics["pros"]


def test_risk_metrics_include_missing_utility_mitigation() -> None:
    plot = make_plot(sewer=False, road_access=False)

    metrics = calculate_risk_metrics(plot)

    assert metrics["overall_risk_score"] >= 0
    assert metrics["risk_level"] in {"Low", "Medium", "High"}
    assert any("utility" in item.lower() for item in metrics["mitigation_suggestions"])


def test_location_metrics_use_landmarks_and_purpose() -> None:
    plot = make_plot()

    metrics = calculate_location_metrics(plot, purpose="residential")

    assert metrics["location_score"] >= 0
    assert metrics["purpose_suitability"] == 10
    assert metrics["best_use"] == "Residential"


def test_search_router_splits_normal_simple_and_full() -> None:
    assert classify_search_query("Dallas") == SearchRoute.NORMAL_SEARCH
    assert (
        classify_search_query("Austin under 100k") == SearchRoute.SIMPLE_AGENTIC_SEARCH
    )
    assert (
        classify_search_query("recommend the best investment under 100k")
        == SearchRoute.FULL_AGENTIC_SEARCH
    )


def test_question_router_routes_specialists() -> None:
    assert classify_question("Is this a good investment?") == QuestionRoute.INVESTMENT
    assert classify_question("What flood risks exist?") == QuestionRoute.RISK
    assert classify_question("What is nearby?") == QuestionRoute.LOCATION
    assert classify_question("What does the brochure say?") == QuestionRoute.DOCUMENT
