from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app.models import Plot
from app.sorting import SortOption, apply_plot_sort
import re


@dataclass(slots=True)
class PlotSearchFilters:
    keyword: str | None = None
    city: str | None = None
    state: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_area: float | None = None
    max_area: float | None = None
    zoning_type: str | None = None
    listing_type: str | None = None
    status: str | None = None
    road_access: bool | None = None
    water_access: bool | None = None
    electricity: bool | None = None
    sewer: bool | None = None


def apply_plot_filters(query: Query, filters: PlotSearchFilters) -> Query:
    """Apply deterministic, structured filters to a Plot SQLAlchemy query."""
    if filters.city:
        query = query.filter(Plot.city.ilike(f"%{filters.city.strip()}%"))
    if filters.state:
        query = query.filter(Plot.state.ilike(f"%{filters.state.strip()}%"))
    if filters.min_price is not None:
        query = query.filter(Plot.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.filter(Plot.price <= filters.max_price)
    if filters.min_area is not None:
        query = query.filter(Plot.area_acres >= filters.min_area)
    if filters.max_area is not None:
        query = query.filter(Plot.area_acres <= filters.max_area)
    if filters.zoning_type:
        query = query.filter(Plot.zoning_type.ilike(f"%{filters.zoning_type.strip()}%"))
    if filters.listing_type:
        query = query.filter(Plot.listing_type == filters.listing_type)
    if filters.status:
        query = query.filter(Plot.status == filters.status)
    if filters.road_access is not None:
        query = query.filter(Plot.road_access.is_(filters.road_access))
    if filters.water_access is not None:
        query = query.filter(Plot.water_access.is_(filters.water_access))
    if filters.electricity is not None:
        query = query.filter(Plot.electricity.is_(filters.electricity))
    if filters.sewer is not None:
        query = query.filter(Plot.sewer.is_(filters.sewer))

    keyword = filters.keyword.strip() if filters.keyword else ""

    if keyword:
        filler_words = {
            "land",
            "plot",
            "plots",
            "property",
            "properties",
            "for",
            "in",
            "near",
            "at",
            "show",
            "me",
            "find",
            "looking",
            "search",
            "searching",
            "want",
            "need",
            "with",
            "without",
            "and",
            "or",
            "a",
            "an",
            "the",
            "to",
        }

        keywords = [
            word
            for word in re.findall(r"[a-zA-Z0-9]+", keyword.lower())
            if len(word) > 1 and word not in filler_words
        ]

        if keywords:
            for word in keywords:
                pattern = f"%{word}%"

                query = query.filter(
                    or_(
                        Plot.title.ilike(pattern),
                        Plot.description.ilike(pattern),
                        Plot.city.ilike(pattern),
                        Plot.state.ilike(pattern),
                        Plot.zoning_type.ilike(pattern),
                        Plot.listing_type.ilike(pattern),
                        Plot.status.ilike(pattern),
                        Plot.nearby_landmarks.ilike(pattern),
                        Plot.ideal_for.ilike(pattern),
                        Plot.risk_notes.ilike(pattern),
                    )
                )

    return query


def search_plots(
    db: Session,
    filters: PlotSearchFilters,
    sort_by: SortOption = SortOption.BEST_MATCH,
) -> list[Plot]:
    query = apply_plot_filters(db.query(Plot), filters)
    return apply_plot_sort(query, sort_by).all()
