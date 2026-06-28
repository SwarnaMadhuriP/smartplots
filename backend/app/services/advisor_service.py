from app.advisor.schemas import GoalPreferences
from app.models import Plot


def advisor_preflight_notices(
    plots: list[Plot], preferences: GoalPreferences
) -> list[str]:
    notices: list[str] = []
    preferred_location = preferences.preferred_location

    if preferred_location:
        location_words = preferred_location.strip().lower().split()
        has_location_match = any(
            any(word in f"{plot.city} {plot.state}".lower() for word in location_words)
            for plot in plots
        )

        if not has_location_match:
            notices.append(
                f"No exact matches found in {preferred_location}. Showing closest available alternatives instead."
            )

    return notices


def advisor_runtime_error_detail(error: RuntimeError) -> str:
    err_str = str(error)
    err_lower = err_str.lower()

    if "quota" in err_lower or "RESOURCE_EXHAUSTED" in err_str:
        return (
            "Daily AI quota reached. Please try again tomorrow or upgrade your API key."
        )

    if (
        "503" in err_str
        or "unavailable" in err_lower
        or "overloaded" in err_lower
        or "high demand" in err_lower
        or "model is currently experiencing" in err_lower
    ):
        return "The AI advisor is temporarily busy due to high demand. Please try again in a few minutes."

    return err_str
