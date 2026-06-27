from __future__ import annotations

from enum import StrEnum


class SearchRoute(StrEnum):
    NORMAL_SEARCH = "normal_search"
    SIMPLE_AGENTIC_SEARCH = "simple_agentic_search"
    FULL_AGENTIC_SEARCH = "full_agentic_search"


class QuestionRoute(StrEnum):
    INVESTMENT = "investment"
    RISK = "risk"
    LOCATION = "location"
    DOCUMENT = "document"
    RECOMMENDATION = "recommendation"


def classify_search_query(query: str) -> SearchRoute:
    text = query.strip().lower()
    if not text:
        return SearchRoute.NORMAL_SEARCH

    words = text.split()
    has_numbers = any(char.isdigit() for char in text)
    filter_keywords = {
        "under",
        "over",
        "above",
        "below",
        "less",
        "more",
        "between",
        "acres",
        "acre",
        "budget",
        "near",
        "with",
        "without",
        "cheap",
        "affordable",
        "farmland",
        "commercial",
        "residential",
        "agricultural",
        "camping",
        "farming",
        "water",
        "road",
        "electricity",
        "sewer",
        "power",
    }
    full_agentic_keywords = {
        "recommend",
        "best",
        "why",
        "compare",
        "tradeoff",
        "tradeoffs",
        "risk",
        "investment",
        "appreciation",
        "roi",
        "return",
        "documents",
        "document",
        "brochure",
        "report",
        "records",
        "zoning",
        "hoa",
        "flood",
        "build",
        "develop",
        "due diligence",
    }

    if any(keyword in text for keyword in full_agentic_keywords):
        return SearchRoute.FULL_AGENTIC_SEARCH
    if (
        len(words) <= 2
        and not has_numbers
        and not any(keyword in text for keyword in filter_keywords)
    ):
        return SearchRoute.NORMAL_SEARCH
    return SearchRoute.SIMPLE_AGENTIC_SEARCH


def classify_question(question: str) -> QuestionRoute:
    text = question.strip().lower()

    document_keywords = {
        "document",
        "documents",
        "brochure",
        "report",
        "records",
        "record",
        "disclosure",
        "deed",
        "title",
        "hoa",
        "zoning report",
        "soil report",
        "utility report",
        "source",
        "cite",
        "citation",
    }
    investment_keywords = {
        "investment",
        "price",
        "value",
        "appreciation",
        "return",
        "roi",
        "budget",
        "profit",
        "rental",
        "resale",
        "afford",
        "financial",
    }
    risk_keywords = {
        "risk",
        "risks",
        "flood",
        "hazard",
        "problem",
        "concern",
        "mitigate",
        "mitigation",
        "restriction",
        "zoning",
        "utilities",
        "utility",
        "sewer",
        "water",
        "electric",
        "road",
    }
    location_keywords = {
        "location",
        "near",
        "nearby",
        "landmark",
        "access",
        "accessibility",
        "city",
        "area",
        "neighborhood",
        "suitable",
        "best use",
        "use",
    }

    if any(keyword in text for keyword in document_keywords):
        return QuestionRoute.DOCUMENT
    if any(keyword in text for keyword in investment_keywords):
        return QuestionRoute.INVESTMENT
    if any(keyword in text for keyword in risk_keywords):
        return QuestionRoute.RISK
    if any(keyword in text for keyword in location_keywords):
        return QuestionRoute.LOCATION
    return QuestionRoute.RECOMMENDATION
