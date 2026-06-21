from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base, get_db
from .models import Plot
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Literal
from app.prompts import ANALYZE_PROMPT
import os, json, re, uuid
from sqlalchemy import or_


# Google GenAI client helper
def get_genai_client():
    from google import genai

    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True") == "True"
    # Fallback to API key if no GCP auth is found
    if use_vertex:
        try:
            import google.auth

            google.auth.default()
        except Exception:
            os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
            use_vertex = False

    if use_vertex:
        return genai.Client(vertexai=True, location="global")
    else:
        # Fallback to GEMINI_API_KEY if GOOGLE_API_KEY is not set
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not os.environ.get("GOOGLE_API_KEY") and gemini_key is not None:
            os.environ["GOOGLE_API_KEY"] = gemini_key
        return genai.Client(vertexai=False)


app = FastAPI(title="SmartPlots API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


# fetch all plots
@app.get("/plots")
def get_plots(search: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Plot)

    if search:
        search_lower = search.lower().strip()

        # Example: "between 30k and 50k"
        between_match = re.search(
            r"between\s+(\d+)\s*(k)?\s+and\s+(\d+)\s*(k)?",
            search_lower,
        )

        if between_match:
            min_price = int(between_match.group(1))
            max_price = int(between_match.group(3))

            if between_match.group(2) == "k":
                min_price *= 1000

            if between_match.group(4) == "k":
                max_price *= 1000

            query = query.filter(Plot.price >= min_price, Plot.price <= max_price)
            search_lower = search_lower.replace(between_match.group(0), "")

        # Example: "under 50k", "below 50k", "less than 50k"
        max_match = re.search(
            r"(under|below|less than)\s+(\d+)\s*(k)?",
            search_lower,
        )

        if max_match:
            max_price = int(max_match.group(2))

            if max_match.group(3) == "k":
                max_price *= 1000

            query = query.filter(Plot.price <= max_price)
            search_lower = search_lower.replace(max_match.group(0), "")

        # Example: "above 30k", "over 30k", "greater than 30k"
        min_match = re.search(
            r"(above|over|greater than|more than)\s+(\d+)\s*(k)?",
            search_lower,
        )

        if min_match:
            min_price = int(min_match.group(2))

            if min_match.group(3) == "k":
                min_price *= 1000

            query = query.filter(Plot.price >= min_price)
            search_lower = search_lower.replace(min_match.group(0), "")

        filler_words = {
            "land",
            "plot",
            "plots",
            "for",
            "in",
            "near",
            "at",
            "show",
            "me",
            "find",
            "looking",
            "want",
            "with",
            "than",
        }

        keywords = [
            word
            for word in search_lower.split()
            if word not in filler_words and not word.replace("k", "").isdigit()
        ]

        for word in keywords:
            query = query.filter(
                or_(
                    Plot.city.ilike(f"%{word}%"),
                    Plot.state.ilike(f"%{word}%"),
                    Plot.title.ilike(f"%{word}%"),
                    Plot.zoning_type.ilike(f"%{word}%"),
                    Plot.ideal_for.ilike(f"%{word}%"),
                )
            )

    plots = query.all()

    result = []

    for plot in plots:
        primary_image = None

        if plot.images:
            primary = next(
                (img for img in plot.images if img.is_primary),
                plot.images[0],
            )
            primary_image = primary.image_url

        reasons = []

        if plot.road_access:
            reasons.append("Road access is available")

        if plot.water_access:
            reasons.append("Water access is available")

        if plot.electricity:
            reasons.append("Electricity connection is available")

        if plot.zoning_type:
            reasons.append(f"Zoned for {plot.zoning_type.lower()} use")

        if plot.ideal_for:
            reasons.append(f"Suitable for {plot.ideal_for}")

        if not reasons:
            reasons.append("Matches basic land search criteria")

        result.append(
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
                "matchScore": plot.insight.investment_score if plot.insight else 7,
                "appreciation": plot.insight.growth_potential
                if plot.insight
                else "Moderate",
                "rentalDemand": "High",
                "liquidity": "Good",
                "riskLevel": plot.insight.risk_level if plot.insight else "Medium",
                "reasons": reasons[:3],
                "highlights": [item.strip() for item in plot.ideal_for.split(",")]
                if plot.ideal_for
                else ["Suitable for residential or investment use"],
            }
        )

    return result


@app.get("/plots/{plot_id}")
def get_plot(plot_id: int, db: Session = Depends(get_db)):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()

    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    return {
        "id": plot.id,
        "title": plot.title,
        "description": plot.description,
        "price": plot.price,
        "area_acres": plot.area_acres,
        "city": plot.city,
        "state": plot.state,
        "zoning_type": plot.zoning_type,
        "road_access": plot.road_access,
        "water_access": plot.water_access,
        "electricity": plot.electricity,
        "nearby_landmarks": plot.nearby_landmarks,
        "ideal_for": plot.ideal_for,
        "risk_notes": plot.risk_notes,
        "images": [img.image_url for img in plot.images],
    }


class AnalyzeRequest(BaseModel):
    question: str | None = None


class AnalysisSchema(BaseModel):
    investment_score: int = Field(..., description="Investment score between 0 and 10")
    risk_level: Literal["Low", "Medium", "High"]
    growth_potential: Literal["Low", "Medium", "High"]
    summary: str
    reasons: List[str]
    pros: List[str]
    cons: List[str]


@app.post("/plots/{plot_id}/analyze")
def analyze_plot(plot_id: int, request: AnalyzeRequest, db: Session = Depends(get_db)):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()

    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    question = request.question or "Analyze this plot for investment potential."
    price_per_acre = plot.price / plot.area_acres if plot.area_acres > 0 else None

    prompt = ANALYZE_PROMPT.format(
        question=question,
        title=plot.title,
        city=plot.city,
        state=plot.state,
        price=plot.price,
        area=plot.area_acres,
        price_per_acre=price_per_acre if price_per_acre else "N/A",
        zoning=plot.zoning_type or "N/A",
        road="Yes" if plot.road_access else "No",
        water="Yes" if plot.water_access else "No",
        electricity="Yes" if plot.electricity else "No",
        sewer="Yes" if plot.sewer else "No",
        ideal_for=plot.ideal_for or "N/A",
        risk_notes=plot.risk_notes or "N/A",
    )

    try:
        from google.genai import types

        genai_client = get_genai_client()

        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalysisSchema,
                temperature=0.2,
            ),
        )

        if response.text is None:
            raise ValueError("Response text is empty")
        data = json.loads(response.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "plot_id": plot.id,
        "investment_score": data.get("investment_score"),
        "risk_level": data.get("risk_level"),
        "growth_potential": data.get("growth_potential"),
        "summary": data.get("summary"),
        "reasons": data.get("reasons", []),
        "pros": data.get("pros", []),
        "cons": data.get("cons", []),
    }


class SmartSearchRequest(BaseModel):
    query: str


@app.post("/ai/search")
async def ai_search(request: SmartSearchRequest):
    from app.agent import root_agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types as adk_types

    session_id = str(uuid.uuid4())
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="user", session_id=session_id
    )
    runner = Runner(agent=root_agent, app_name="app", session_service=session_service)

    response_text = ""
    async for event in runner.run_async(
        user_id="user",
        session_id=session_id,
        new_message=adk_types.Content(
            role="user", parts=[adk_types.Part.from_text(text=request.query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response_text = event.content.parts[0].text or ""

    session = await session_service.get_session(
        app_name="app", user_id="user", session_id=session_id
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    ranked_plots = session.state.get("ranked_plots", [])
    filters = session.state.get("filters", {})

    return {
        "response": response_text,
        "plots": ranked_plots,
        "filters": filters,
    }
