from __future__ import annotations

from enum import StrEnum
from typing import Any

from sqlalchemy.orm import Query

from app.models import Plot


class SortOption(StrEnum):
    BEST_MATCH = "best_match"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    ACRES_ASC = "acres_asc"
    ACRES_DESC = "acres_desc"
    NEWEST = "newest"
    AI_INVESTMENT_SCORE = "ai_investment_score"


def apply_plot_sort(query: Query, sort_by: SortOption) -> Query:
    if sort_by == SortOption.PRICE_ASC:
        return query.order_by(Plot.price.asc())
    if sort_by == SortOption.PRICE_DESC:
        return query.order_by(Plot.price.desc())
    if sort_by == SortOption.ACRES_ASC:
        return query.order_by(Plot.area_acres.asc())
    if sort_by == SortOption.ACRES_DESC:
        return query.order_by(Plot.area_acres.desc())
    if sort_by == SortOption.NEWEST:
        return query.order_by(Plot.created_at.desc().nullslast())
    if sort_by == SortOption.AI_INVESTMENT_SCORE:
        return query.order_by(Plot.id.asc())
    return query


def _number(value: Any) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").replace("Acres", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0
    return 0


def sort_plot_dicts(plots: list[dict], sort_by: SortOption) -> list[dict]:
    if sort_by == SortOption.PRICE_ASC:
        return sorted(
            plots, key=lambda plot: _number(plot.get("rawPrice") or plot.get("price"))
        )
    if sort_by == SortOption.PRICE_DESC:
        return sorted(
            plots,
            key=lambda plot: _number(plot.get("rawPrice") or plot.get("price")),
            reverse=True,
        )
    if sort_by == SortOption.ACRES_ASC:
        return sorted(
            plots, key=lambda plot: _number(plot.get("rawAcres") or plot.get("acres"))
        )
    if sort_by == SortOption.ACRES_DESC:
        return sorted(
            plots,
            key=lambda plot: _number(plot.get("rawAcres") or plot.get("acres")),
            reverse=True,
        )
    if sort_by == SortOption.NEWEST:
        return sorted(
            plots,
            key=lambda plot: str(plot.get("createdAt") or ""),
            reverse=True,
        )
    if sort_by == SortOption.AI_INVESTMENT_SCORE:
        return sorted(
            plots,
            key=lambda plot: _number(
                plot.get("aiInvestmentScore")
                or plot.get("investmentScore")
                or plot.get("matchScore")
            ),
            reverse=True,
        )
    return plots
