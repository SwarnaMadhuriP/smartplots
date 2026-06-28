from __future__ import annotations

from enum import StrEnum


class SearchRoute(StrEnum):
    DB_SEARCH = "db_search"
    AI_SEARCH = "ai_search"


class QuestionRoute(StrEnum):
    INVESTMENT = "investment"
    RISK = "risk"
    LOCATION = "location"
    DOCUMENT = "document"
    RECOMMENDATION = "recommendation"


ASK_SPECIALIST_LIMIT = 2


def classify_search_query(query: str) -> SearchRoute:
    if not query.strip():
        return SearchRoute.DB_SEARCH

    return SearchRoute.AI_SEARCH


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


def select_ask_specialists(question: str) -> list[QuestionRoute]:
    text = question.strip().lower()
    selected: list[QuestionRoute] = []

    def add(route: QuestionRoute) -> None:
        if route not in selected and len(selected) < ASK_SPECIALIST_LIMIT:
            selected.append(route)

    broad_purchase = any(
        phrase in text
        for phrase in [
            "should i buy",
            "should we buy",
            "worth buying",
            "recommend",
            "good deal",
        ]
    )
    comparison_use = any(word in text for word in ["better", "best", "versus", "vs"])

    if broad_purchase:
        add(QuestionRoute.INVESTMENT)
        add(QuestionRoute.RISK)
        return selected

    location_terms = {
        "location",
        "near",
        "nearby",
        "landmark",
        "access",
        "area",
        "neighborhood",
        "suitable",
        "best use",
        "use",
        "airbnb",
        "home",
        "build",
        "building",
    }
    investment_terms = {
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
    risk_terms = {
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

    if any(term in text for term in location_terms):
        add(QuestionRoute.LOCATION)
    if comparison_use:
        add(QuestionRoute.INVESTMENT)
    if any(term in text for term in investment_terms):
        add(QuestionRoute.INVESTMENT)
    if any(term in text for term in risk_terms):
        add(QuestionRoute.RISK)

    route = classify_question(question)
    if route in {
        QuestionRoute.INVESTMENT,
        QuestionRoute.RISK,
        QuestionRoute.LOCATION,
    }:
        add(route)

    return selected[:ASK_SPECIALIST_LIMIT]
