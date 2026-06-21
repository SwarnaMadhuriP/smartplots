import os
import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.tools import ToolContext
from app.database import SessionLocal
from app.models import Plot
from sqlalchemy import or_

# Handle GCP auth and environment variables gracefully
try:
    _, project_id = google.auth.default()
    if not project_id:
        project_id = "mock-project-id"
except Exception:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "mock-project-id")

os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

# Check if we should use Vertex AI or AI Studio
use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")
if use_vertex is None:
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
    else:
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "False":
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not os.environ.get("GOOGLE_API_KEY") and gemini_key is not None:
        os.environ["GOOGLE_API_KEY"] = gemini_key


def search_and_score_plots(
    query: str,
    city: str | None = None,
    max_price: float | None = None,
    zoning: str | None = None,
    purpose: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict:
    """Searches for land plots in the database and ranks them based on user preferences.

    Args:
        query: General keywords to search for in title, description, or ideal uses.
        city: Optional city name to filter by (e.g. Austin, Dallas, Houston).
        max_price: Optional maximum price budget.
        zoning: Optional zoning type (e.g. residential, commercial, agricultural).
        purpose: Optional purpose of land use (e.g. camping, vacation, farming).

    Returns:
        A dict containing status and count of matched plots.
    """
    db = SessionLocal()
    try:
        db_query = db.query(Plot)

        # Apply structured filters if provided
        if city:
            db_query = db_query.filter(Plot.city.ilike(f"%{city}%"))
        if max_price:
            db_query = db_query.filter(Plot.price <= max_price)
        if zoning:
            db_query = db_query.filter(Plot.zoning_type.ilike(f"%{zoning}%"))

        # Keyword search
        if query:
            keywords = [
                word
                for word in query.lower().split()
                if word not in ["land", "plot", "plots", "for", "in", "near", "at"]
            ]
            for word in keywords:
                db_query = db_query.filter(
                    or_(
                        Plot.city.ilike(f"%{word}%"),
                        Plot.state.ilike(f"%{word}%"),
                        Plot.title.ilike(f"%{word}%"),
                        Plot.zoning_type.ilike(f"%{word}%"),
                        Plot.ideal_for.ilike(f"%{word}%"),
                    )
                )

        plots_from_db = db_query.all()
        ranked_plots = []

        for plot in plots_from_db:
            score = 60
            reasons = []

            if plot.road_access:
                score += 10
                reasons.append("Road access is available")

            if plot.water_access:
                score += 10
                reasons.append("Water access is available")

            if plot.electricity:
                score += 10
                reasons.append("Electricity connection is available")

            if max_price and plot.price <= max_price:
                score += 10
                reasons.append("Fits your budget preference")

            if purpose and purpose.lower() == "camping":
                ideal_for = (plot.ideal_for or "").lower()
                if "camping" in ideal_for:
                    score += 15
                    reasons.append("Matches your camping preference")

            primary_image = None
            if plot.images:
                primary = next(
                    (img for img in plot.images if img.is_primary), plot.images[0]
                )
                primary_image = primary.image_url

            ranked_plots.append(
                {
                    "id": plot.id,
                    "title": plot.title,
                    "description": plot.description,
                    "image": primary_image or "/placeholder-plot.jpg",
                    "location": f"{plot.city}, {plot.state}",
                    "latitude": plot.latitude,
                    "longitude": plot.longitude,
                    "price": f"${int(plot.price):,}",
                    "acres": f"{plot.area_acres} Acres",
                    "zone": plot.zoning_type or "General",
                    "matchScore": min(score, 100),
                    "appreciation": plot.insight.growth_potential
                    if plot.insight
                    else "Moderate",
                    "rentalDemand": "High",
                    "liquidity": "Good",
                    "riskLevel": plot.insight.risk_level if plot.insight else "Medium",
                    "reasons": reasons[:3] or ["Matches your search preferences"],
                    "highlights": [item.strip() for item in plot.ideal_for.split(",")]
                    if plot.ideal_for
                    else ["Suitable for residential or investment use"],
                    "city": plot.city,
                    "state": plot.state,
                    "rawPrice": plot.price,
                    "rawAcres": plot.area_acres,
                }
            )

        # Sort by match score descending
        ranked_plots.sort(key=lambda p: p["matchScore"], reverse=True)

        if tool_context:
            tool_context.state["ranked_plots"] = ranked_plots
            tool_context.state["filters"] = {
                "city": city,
                "max_price": max_price,
                "zoning": zoning,
                "purpose": purpose,
            }

        return {"status": "success", "count": len(ranked_plots)}
    finally:
        db.close()


root_agent = Agent(
    name="smartplots_agent",
    model="gemini-2.5-flash",
    instruction="""You are a concierge land advisor for SmartPlots. 
    You help users search for and evaluate land plots based on their preferences.
    Use the search_and_score_plots tool to fetch real properties from the database.
    After fetching the plots, summarize why the top matches fit the user's needs in a friendly, professional response.
    Never invent plots or features that are not in the database.""",
    tools=[search_and_score_plots],
)

app = App(
    root_agent=root_agent,
    name="app",
)
