from __future__ import annotations

from dataclasses import dataclass, replace

from sqlalchemy import false, or_
from sqlalchemy.orm import Query, Session

from app.models import Plot
from app.services.sorting_service import SortOption, apply_plot_sort
import re

STATE_ALIASES = {
    "al": "AL",
    "alabama": "AL",
    "ak": "AK",
    "alaska": "AK",
    "az": "AZ",
    "arizona": "AZ",
    "ar": "AR",
    "arkansas": "AR",
    "ca": "CA",
    "california": "CA",
    "co": "CO",
    "colorado": "CO",
    "ct": "CT",
    "connecticut": "CT",
    "de": "DE",
    "delaware": "DE",
    "fl": "FL",
    "florida": "FL",
    "ga": "GA",
    "georgia": "GA",
    "hi": "HI",
    "hawaii": "HI",
    "id": "ID",
    "idaho": "ID",
    "il": "IL",
    "illinois": "IL",
    "in": "IN",
    "indiana": "IN",
    "ia": "IA",
    "iowa": "IA",
    "ks": "KS",
    "kansas": "KS",
    "ky": "KY",
    "kentucky": "KY",
    "la": "LA",
    "louisiana": "LA",
    "me": "ME",
    "maine": "ME",
    "md": "MD",
    "maryland": "MD",
    "ma": "MA",
    "massachusetts": "MA",
    "mi": "MI",
    "michigan": "MI",
    "mn": "MN",
    "minnesota": "MN",
    "ms": "MS",
    "mississippi": "MS",
    "mo": "MO",
    "missouri": "MO",
    "mt": "MT",
    "montana": "MT",
    "ne": "NE",
    "nebraska": "NE",
    "nv": "NV",
    "nevada": "NV",
    "nh": "NH",
    "new hampshire": "NH",
    "nj": "NJ",
    "new jersey": "NJ",
    "nm": "NM",
    "new mexico": "NM",
    "ny": "NY",
    "new york": "NY",
    "nc": "NC",
    "north carolina": "NC",
    "nd": "ND",
    "north dakota": "ND",
    "oh": "OH",
    "ohio": "OH",
    "ok": "OK",
    "oklahoma": "OK",
    "or": "OR",
    "oregon": "OR",
    "pa": "PA",
    "pennsylvania": "PA",
    "ri": "RI",
    "rhode island": "RI",
    "sc": "SC",
    "south carolina": "SC",
    "sd": "SD",
    "south dakota": "SD",
    "tn": "TN",
    "tennessee": "TN",
    "tx": "TX",
    "texas": "TX",
    "ut": "UT",
    "utah": "UT",
    "vt": "VT",
    "vermont": "VT",
    "va": "VA",
    "virginia": "VA",
    "wa": "WA",
    "washington": "WA",
    "wv": "WV",
    "west virginia": "WV",
    "wi": "WI",
    "wisconsin": "WI",
    "wy": "WY",
    "wyoming": "WY",
}

SEARCH_FILLER_WORDS = {
    "land",
    "lot",
    "lots",
    "plot",
    "plots",
    "property",
    "properties",
    "area",
    "areas",
    "zone",
    "zones",
    "for",
    "in",
    "near",
    "at",
    "around",
    "show",
    "me",
    "find",
    "looking",
    "search",
    "searching",
    "want",
    "need",
    "that",
    "have",
    "has",
    "access",
    "with",
    "without",
    "and",
    "or",
    "a",
    "an",
    "the",
    "to",
}


@dataclass(slots=True)
class PlotSearchFilters:
    search_term: str | None = None
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
    candidate_ids: list[int] | None = None


def parse_number(value: str, suffix: str | None = None) -> float | None:
    try:
        number = float(value.replace(",", ""))
    except ValueError:
        return None

    if suffix and suffix.lower() == "k":
        return number * 1_000
    if suffix and suffix.lower() == "m":
        return number * 1_000_000
    return number


def extract_search_term(query: str) -> str | None:
    """Return a concise keyword term when the query has no structured filters."""
    keywords = [
        word
        for word in re.findall(r"[a-zA-Z0-9]+", query.lower())
        if len(word) > 1 and word not in SEARCH_FILLER_WORDS
    ]
    return " ".join(keywords) if keywords else None


def extract_query_filters(query: str, filters: PlotSearchFilters) -> PlotSearchFilters:
    """Extract common natural-language filters for DB fallback searches."""
    text = query.strip().lower()
    if not text:
        return filters

    extracted = False
    next_filters = replace(filters)

    if next_filters.state is None:
        for alias, abbreviation in STATE_ALIASES.items():
            is_abbreviation = len(alias) == 2
            pattern = (
                rf"\b(?:in|near|around)\s+{re.escape(alias)}\b"
                if is_abbreviation
                else rf"\b{re.escape(alias)}\b"
            )
            if re.search(pattern, text):
                next_filters.state = abbreviation
                extracted = True
                break

    max_price_match = re.search(
        r"\b(?:under|below|less than|max(?:imum)?|budget(?: of)?)\s+\$?([\d,.]+)\s*([km])?\b",
        text,
    )
    if next_filters.max_price is None and max_price_match:
        max_price = parse_number(max_price_match.group(1), max_price_match.group(2))
        if max_price is not None:
            next_filters.max_price = max_price
            extracted = True

    min_price_match = re.search(
        r"\b(?:over|above|more than|min(?:imum)?)\s+\$?([\d,.]+)\s*([km])?\b",
        text,
    )
    if next_filters.min_price is None and min_price_match:
        min_price = parse_number(min_price_match.group(1), min_price_match.group(2))
        if min_price is not None:
            next_filters.min_price = min_price
            extracted = True

    max_area_match = re.search(
        r"\b(?:under|below|less than|max(?:imum)?)\s+([\d,.]+)\s*(?:acres|acre)\b",
        text,
    )
    if next_filters.max_area is None and max_area_match:
        max_area = parse_number(max_area_match.group(1))
        if max_area is not None:
            next_filters.max_area = max_area
            extracted = True

    min_area_match = re.search(
        r"\b(?:over|above|more than|min(?:imum)?)\s+([\d,.]+)\s*(?:acres|acre)\b",
        text,
    )
    if next_filters.min_area is None and min_area_match:
        min_area = parse_number(min_area_match.group(1))
        if min_area is not None:
            next_filters.min_area = min_area
            extracted = True

    utility_terms = {
        "road_access": ("road", "road access"),
        "water_access": ("water", "water access"),
        "electricity": ("electricity", "power"),
        "sewer": ("sewer",),
    }
    for field_name, terms in utility_terms.items():
        if getattr(next_filters, field_name) is not None:
            continue

        if any(f"without {term}" in text for term in terms):
            setattr(next_filters, field_name, False)
            extracted = True
        elif any(term in text for term in terms):
            setattr(next_filters, field_name, True)
            extracted = True

    zoning_terms = ("residential", "commercial", "agricultural")
    if next_filters.zoning_type is None:
        for zoning_type in zoning_terms:
            if zoning_type in text:
                next_filters.zoning_type = zoning_type.title()
                extracted = True
                break

    city_match = re.search(
        r"\bin\s+([a-z][a-z\s]+?)(?=\s+(?:with|without|under|over|above|below|less|more|between|near|for|and|\d)|$)",
        text,
    )
    if next_filters.city is None and city_match:
        city_text = city_match.group(1).strip()
        city_words = set(re.findall(r"[a-z]+", city_text))
        non_city_words = {
            "area",
            "zone",
            "zoned",
            "zoning",
            "land",
            "plot",
            "plots",
            "property",
            "properties",
            "residential",
            "commercial",
            "agricultural",
        }
        if (
            city_text
            and city_text.lower() not in STATE_ALIASES
            and not city_words.intersection(non_city_words)
        ):
            next_filters.city = city_text.title()
            extracted = True

    if extracted:
        next_filters.search_term = None
    elif next_filters.search_term is None:
        next_filters.search_term = extract_search_term(query)

    return next_filters


def apply_plot_filters(query: Query, filters: PlotSearchFilters) -> Query:
    """Apply deterministic, structured filters to a Plot SQLAlchemy query."""
    if filters.candidate_ids is not None:
        if not filters.candidate_ids:
            return query.filter(false())
        query = query.filter(Plot.id.in_(filters.candidate_ids))
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

    keyword = filters.search_term.strip() if filters.search_term else ""

    if keyword:
        keywords = [
            word
            for word in re.findall(r"[a-zA-Z0-9]+", keyword.lower())
            if len(word) > 1 and word not in SEARCH_FILLER_WORDS
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
