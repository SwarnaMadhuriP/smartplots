from app.advisor.schemas import GoalKey
from app.advisor.schemas import GoalPreferences
from app.models import Plot


def advisor_preflight_notices(
    plots: list[Plot],
    goal: GoalKey,
    preferences: GoalPreferences,
) -> list[str]:
    notices: list[str] = []

    if not plots:
        return [
            "No plots matched your current preferences. Try relaxing your budget, location, acreage, or utility requirements."
        ]

    if preferences.preferred_location:
        location = preferences.preferred_location.strip().lower()
        has_location_match = any(
            location in f"{plot.city} {plot.state}".lower()
            or location in f"{plot.city}, {plot.state}".lower()
            for plot in plots
        )

        if not has_location_match:
            notices.append(
                f"No exact matches found in {preferences.preferred_location}. Showing closest available alternatives instead."
            )

    if preferences.budget_max is not None:
        if all(plot.price > preferences.budget_max for plot in plots):
            notices.append(
                "No plots are within your budget. Showing the closest lower-fit alternatives."
            )

    if preferences.min_acres is not None:
        if all(plot.area_acres < preferences.min_acres for plot in plots):
            notices.append(
                "No plots meet your minimum acreage. Showing the largest available options."
            )

    if preferences.road_access_required:
        if all(not plot.road_access for plot in plots):
            notices.append(
                "No plots fully satisfy your road access requirement. Showing the closest available alternatives."
            )

    if goal in {"build_home", "retirement_lifestyle"}:
        required = preferences.utilities_required or []

        missing_any_required = any(
            not plot_matches_required_utilities(plot, required)
            for plot in plots
        )

        if required and missing_any_required:
            notices.append(
                "Some plots may not include all required utilities. Review utility details before deciding."
            )

    if goal == "commercial":
        if preferences.commercial_zoning_required:
            if all(plot.zoning_type != "commercial" for plot in plots):
                notices.append(
                    "No commercial-zoned plots were found. Showing the closest alternatives."
                )

    if goal == "maximize_value":
        if preferences.price_per_acre_priority:
            notices.append(
                "Recommendations are prioritized by lowest price per acre, but utility and access tradeoffs may still apply."
            )

    return notices[:4]

def plot_matches_required_utilities(plot: Plot, required: list[str]) -> bool:
    utility_map = {
        "water": plot.water_access,
        "electricity": plot.electricity,
        "sewer": getattr(plot, "sewer", False),
    }

    return all(utility_map.get(utility.lower(), False) for utility in required)


def advisor_runtime_error_detail(error: RuntimeError) -> str:
    err_str = str(error)
    err_lower = err_str.lower()

    # Quota / rate limits
    if (
        "quota" in err_lower
        or "resource_exhausted" in err_lower
        or "429" in err_str
        or "rate limit" in err_lower
    ):
        return (
            "The AI advisor has reached its usage limit. Please try again later or use an API key with additional quota."
        )

    # Temporary service issues
    if (
        "503" in err_str
        or "unavailable" in err_lower
        or "overloaded" in err_lower
        or "high demand" in err_lower
        or "temporarily unavailable" in err_lower
        or "model is currently experiencing" in err_lower
    ):
        return (
            "The AI advisor is temporarily unavailable due to high demand. "
            "Please try again in a few minutes."
        )

    # Timeout
    if (
        "timeout" in err_lower
        or "deadline exceeded" in err_lower
        or "timed out" in err_lower
    ):
        return (
            "The AI advisor took too long to respond. Please try again."
        )

    # Network / connectivity
    if (
        "connection" in err_lower
        or "network" in err_lower
        or "dns" in err_lower
    ):
        return (
            "Unable to connect to the AI service. Please check your connection and try again."
        )

    # Unknown error
    return (
        "An unexpected error occurred while generating recommendations. "
        "Please try again."
    )
