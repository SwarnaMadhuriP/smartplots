from app.database import SessionLocal
from app.repositories.plot_search_repository import (
    PlotSearchFilters,
    extract_query_filters,
    search_plots,
)
from app.agents.context import ToolContext
from app.services.plot_embedding_service import semantic_plot_ids


def _build_active_filters(
    search_term: str | None,
    city: str | None,
    state: str | None,
    min_price: float | None,
    max_price: float | None,
    min_area: float | None,
    max_area: float | None,
    zoning_type: str | None,
    listing_type: str | None,
    status: str | None,
    road_access: bool | None,
    water_access: bool | None,
    electricity: bool | None,
    sewer: bool | None,
    purpose: str | None,
) -> dict:
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
    return {
        key: value
        for key, value in active_filters.items()
        if value not in (None, "")
    }


def _active_filters_from_search_filters(
    filters: PlotSearchFilters,
    purpose: str | None,
) -> dict:
    return _build_active_filters(
        filters.search_term,
        filters.city,
        filters.state,
        filters.min_price,
        filters.max_price,
        filters.min_area,
        filters.max_area,
        filters.zoning_type,
        filters.listing_type,
        filters.status,
        filters.road_access,
        filters.water_access,
        filters.electricity,
        filters.sewer,
        purpose,
    )


def _rank_plots(plots_from_db, purpose: str | None, semantic_order: list[int] | None = None) -> list[dict]:
    semantic_rank = {
        plot_id: index
        for index, plot_id in enumerate(semantic_order or [])
    }
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
        key=lambda p: (
            int(p.get("matchScore", 0)),
            -semantic_rank.get(int(p.get("id", 0)), 10_000),
        ),
        reverse=True,
    )
    return ranked_plots


def semantic_search_and_score_plots(
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
    """Searches plots semantically, applies deterministic filters, and ranks results.

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
        semantic_query = " ".join(
            part for part in [query.strip(), search_term or "", purpose or ""]
            if part
        ).strip()
        candidate_ids = semantic_plot_ids(db, semantic_query, limit=25)
        if not candidate_ids:
            raise ValueError("No plot embeddings are available for semantic search.")

        filters = PlotSearchFilters(
            search_term=None,
            candidate_ids=candidate_ids,
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
        filters = extract_query_filters(query, filters)
        filters.search_term = None
        filters.candidate_ids = candidate_ids

        plots_from_db = search_plots(db, filters)
        ranked_plots = _rank_plots(
            plots_from_db,
            purpose=purpose,
            semantic_order=candidate_ids,
        )

        active_filters = _active_filters_from_search_filters(filters, purpose)
        active_filters["semantic_search"] = True

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

    except Exception as exc:  # noqa: BLE001
        return search_and_score_plots(
            query=query,
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
            purpose=purpose,
            tool_context=tool_context,
            fallback_reason=str(exc),
        )
    finally:
        db.close()


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
    fallback_reason: str | None = None,
) -> dict:
    """Fallback deterministic AI search tool, kept for compatibility."""
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
        filters = extract_query_filters(query, filters)

        plots_from_db = search_plots(db, filters)
        ranked_plots = _rank_plots(plots_from_db, purpose=purpose)
        active_filters = _active_filters_from_search_filters(filters, purpose)
        if fallback_reason:
            active_filters["semantic_fallback"] = True

        if tool_context:
            tool_context.state["ranked_plots"] = ranked_plots
            tool_context.state["filters"] = active_filters
            tool_context.state["query"] = query
            tool_context.state["deterministic_analysis"] = {}

        return {
            "status": "success",
            "count": len(ranked_plots),
        }

    finally:
        db.close()
