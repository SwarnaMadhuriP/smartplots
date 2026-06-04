from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from app.database import SessionLocal
from app.models import Plot


class SmartPlotsState(TypedDict):
    query: str
    filters: dict[str, Any]
    plots: list[dict[str, Any]]
    ranked_plots: list[dict[str, Any]]
    response: str


def parse_query(state: SmartPlotsState):
    query = state["query"].lower()

    filters = {}

    if "austin" in query:
        filters["city"] = "Austin"

    if "under 100k" in query or "under $100k" in query:
        filters["max_price"] = 100000

    if "camping" in query:
        filters["purpose"] = "camping"

    return {"filters": filters}


def retrieve_plots(state: SmartPlotsState):
    db = SessionLocal()

    try:
        query = db.query(Plot)
        filters = state["filters"]

        if filters.get("city"):
            query = query.filter(Plot.city == filters["city"])

        if filters.get("max_price"):
            query = query.filter(Plot.price <= filters["max_price"])

        plots_from_db = query.all()

        plots = []

        for plot in plots_from_db:
            plots.append(
                {
                    "id": plot.id,
                    "title": plot.title,
                    "city": plot.city,
                    "state": plot.state,
                    "price": plot.price,
                    "acres": plot.area_acres,
                    "zoning": plot.zoning_type,
                    "road_access": plot.road_access,
                    "water_access": plot.water_access,
                    "electricity": plot.electricity,
                    "sewer": plot.sewer,
                    "ideal_for": plot.ideal_for,
                    "risk_notes": plot.risk_notes,
                    "image": plot.images[0].image_url if plot.images else None,
                }
            )

        return {"plots": plots}

    finally:
        db.close()


def score_plots(state: SmartPlotsState):
    ranked = []

    for plot in state["plots"]:
        score = 60
        reasons = []

        if plot.get("road_access"):
            score += 10
            reasons.append("Road access is available")

        if plot.get("water_access"):
            score += 10
            reasons.append("Water access is available")

        if plot.get("electricity"):
            score += 10
            reasons.append("Electricity connection is available")

        if plot.get("price") and plot["price"] <= state["filters"].get(
            "max_price", float("inf")
        ):
            score += 10
            reasons.append("Fits your budget preference")

        if state["filters"].get("purpose") == "camping":
            ideal_for = (plot.get("ideal_for") or "").lower()

            if "camping" in ideal_for:
                score += 15
                reasons.append("Matches your camping preference")

        ranked.append(
            {
                "id": plot["id"],
                "title": plot["title"],
                "image": plot.get("image") or "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
                "location": f"{plot['city']}, {plot['state']}",
                "price": f"${plot['price']:,.0f}",
                "acres": f"{plot['acres']} Acres",
                "matchScore": min(score, 100),
                "reasons": reasons
                or ["Matches your search preferences"],
                "highlights": [
                    plot.get("ideal_for")
                    or "Land opportunity",
                    f"{plot['acres']} acres",
                    plot.get("risk_notes")
                    or "Review property details before purchase",
                ],
                "riskLevel": "Medium",
                "city": plot["city"],
                "state": plot["state"],
                "rawPrice": plot["price"],
                "rawAcres": plot["acres"],
            }
        )

    ranked.sort(key=lambda p: p["matchScore"], reverse=True)

    return {"ranked_plots": ranked}


def generate_response(state: SmartPlotsState):
    if not state["ranked_plots"]:
        return {
            "response": "I couldn't find matching plots for your search."
        }

    top = state["ranked_plots"][0]

    response = (
        f"Best match: {top['title']} in {top['location']}.\n"
        f"Price: {top['price']}, Acres: {top['acres']}.\n"
        f"Match score: {top['matchScore']}."
    )

    return {"response": response}


graph = StateGraph(SmartPlotsState)

graph.add_node("parse_query", parse_query)
graph.add_node("retrieve_plots", retrieve_plots)
graph.add_node("score_plots", score_plots)
graph.add_node("generate_response", generate_response)

graph.set_entry_point("parse_query")

graph.add_edge("parse_query", "retrieve_plots")
graph.add_edge("retrieve_plots", "score_plots")
graph.add_edge("score_plots", "generate_response")
graph.add_edge("generate_response", END)

smartplots_graph = graph.compile()