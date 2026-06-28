from app.database import SessionLocal
from app.repositories.plot_search_repository import PlotSearchFilters, search_plots
from app.agents.context import ToolContext


def search_and_score_plots(
    query: str = "",
    search_term: str | None = None,
    city: str | None = None,
    state: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_area: float | None = None,
    max_area: float | None = None,
    zoning_type: str | None = None,
    listing_type: str | None = None,
    status: str | None = None,
    road_access: bool | None = None,
    water_access: bool | None = None,
    electricity: bool | None = None,
    sewer: bool | None = None,
    purpose: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict:
    """Searches for land plots using deterministic filters and ranks results for AI Search.

    This function is intentionally lightweight:
    - No investment analysis
    - No risk analysis
    - No location analysis
    - No document intelligence
    - No A2A

    The LLM should only explain the ranking later. It should not calculate scores.
    """
    db = SessionLocal()

    try:
        filters = PlotSearchFilters(
            search_term=search_term,
            city=city,
            state=state,
            min_price=min_price,
            max_price=max_price,
            min_area=min_area,
            max_area=max_area,
            zoning_type=zoning_type,
            listing_type=listing_type,
            status=status,
            road_access=road_access,
            water_access=water_access,
            electricity=electricity,
            sewer=sewer,
        )

        plots_from_db = search_plots(db, filters)
        ranked_plots = []

        for plot in plots_from_db:
            d = plot.to_json_dict()

            # Keep matchScore deterministic from plot.to_json_dict/search layer.
            # Add small purpose-based boost only when the query has clear intent.
            if purpose:
                purpose_lower = purpose.lower().strip()
                ideal_for = (plot.ideal_for or "").lower()

                if purpose_lower and purpose_lower in ideal_for:
                    d["matchScore"] = min(10, int(d.get("matchScore", 0)) + 1)

                    reason = f"Matches your {purpose_lower} preference"
                    existing_reasons = d.get("reasons", [])

                    if reason not in existing_reasons:
                        d["reasons"] = [reason] + existing_reasons[:2]

            d.update(
                {
                    "city": plot.city,
                    "state": plot.state,
                    "rawPrice": plot.price,
                    "rawAcres": plot.area_acres,
                    "createdAt": (
                        plot.created_at.isoformat() if plot.created_at else None
                    ),
                }
            )

            ranked_plots.append(d)

        ranked_plots.sort(
            key=lambda p: int(p.get("matchScore", 0)),
            reverse=True,
        )

        active_filters = {
            "search_term": search_term,
            "city": city,
            "state": state,
            "min_price": min_price,
            "max_price": max_price,
            "min_area": min_area,
            "max_area": max_area,
            "zoning_type": zoning_type,
            "listing_type": listing_type,
            "status": status,
            "road_access": road_access,
            "water_access": water_access,
            "electricity": electricity,
            "sewer": sewer,
            "purpose": purpose,
        }

        active_filters = {
            key: value
            for key, value in active_filters.items()
            if value not in (None, "")
        }

        if tool_context:
            tool_context.state["ranked_plots"] = ranked_plots
            tool_context.state["filters"] = active_filters
            tool_context.state["query"] = query

            # Keep this key only for backward compatibility.
            # AI Search should not depend on it.
            tool_context.state["deterministic_analysis"] = {}

        return {
            "status": "success",
            "count": len(ranked_plots),
        }

    finally:
        db.close()
