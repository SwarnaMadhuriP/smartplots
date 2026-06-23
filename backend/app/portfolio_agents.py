import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from app.models import Plot


def get_genai_client():
    from dotenv import load_dotenv

    load_dotenv()
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


class ComparePlotProfile(BaseModel):
    plot_id: int
    award_label: str
    suitability_score: int
    key_tradeoff: str


class ComparisonResponse(BaseModel):
    overall_recommendation: str
    profiles: list[ComparePlotProfile]
    summary_points: list[str]


class MarketReport(BaseModel):
    market_overview: str
    top_picks: list[str]
    critical_risk_alerts: list[str]
    development_readiness_notes: str


def run_comparison_analysis(plots: list[Plot], goal: str | None) -> dict:
    selected_goal = (
        goal
        or "Compare these plots for general investment and residential suitability."
    )

    plots_context = []
    for plot in plots:
        plots_context.append(
            f"""
        - Plot ID: {plot.id}
        - Title: {plot.title}
        - Location: {plot.city}, {plot.state}
        - Price: ${plot.price}
        - Size: {plot.area_acres} acres
        - Zoning: {plot.zoning_type or "General"}
        - Road access: {"Yes" if plot.road_access else "No"}
        - Water access: {"Yes" if plot.water_access else "No"}
        - Electricity: {"Yes" if plot.electricity else "No"}
        - Sewer: {"Yes" if plot.sewer else "No"}
        - Ideal for: {plot.ideal_for or "N/A"}
        - Risk notes: {plot.risk_notes or "N/A"}
        """
        )

    prompt = f"""
    You are a real estate investment analysis agent.
    Compare the following land plots based on the user's specific goal.
    
    User's Goal: {selected_goal}
    
    Plots Data:
    {"".join(plots_context)}
    
    Provide your analysis strictly based on this data. Assign each plot an appropriate single-word or short-phrase award label (e.g. "Best Value", "Best Location", "Most Infrastructure") and a suitability score from 0 to 10 relative to the user's goal.
    """

    try:
        response = genai_client = get_genai_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComparisonResponse,
                temperature=0.2,
            ),
        )
        if response.text is None:
            raise Exception("AI comparison response returned empty content.")
        data = json.loads(response.text)
    except Exception as e:
        raise Exception(f"AI comparison generation failed: {str(e)}")

    return data


def run_market_insights(plots: list[Plot]) -> dict:
    plots_context = []
    for plot in plots:
        plots_context.append(
            f"- Plot ID: {plot.id}, Title: {plot.title}, Price: ${plot.price}, Area: {plot.area_acres} acres, City: {plot.city}, State: {plot.state}, Zoning: {plot.zoning_type or 'General'}, Risk: {plot.risk_notes or 'None'}"
        )

    prompt = f"""
    You are a professional land investment and market analyst.
    Analyze the entire land catalog provided below and generate a structured Market Intelligence Report.
    
    Land Catalog:
    {"\n".join(plots_context)}
    
    Identify top picks based on value (price per acre), highlights, zoning advantages, or development readiness.
    Call out critical risks such as flood hazards, utility gaps, or severe restrictions.
    Summarize overall market trends.
    """

    try:
        response = genai_client = get_genai_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MarketReport,
                temperature=0.2,
            ),
        )
        if response.text is None:
            raise Exception("AI market insights response returned empty content.")
        data = json.loads(response.text)
    except Exception as e:
        raise Exception(f"AI market insights generation failed: {str(e)}")

    return data


def run_catalog_advice(plots: list[Plot], question: str) -> str:
    plots_context = []
    for plot in plots:
        plots_context.append(
            f"- Plot ID: {plot.id}, Title: {plot.title}, Price: ${plot.price}, Area: {plot.area_acres} acres, City: {plot.city}, State: {plot.state}, Zoning: {plot.zoning_type or 'General'}, Road Access: {plot.road_access}, Water Access: {plot.water_access}, Electricity: {plot.electricity}, Sewer: {plot.sewer}, Ideal For: {plot.ideal_for or 'N/A'}, Risk Notes: {plot.risk_notes or 'None'}"
        )

    prompt = f"""
    You are an expert land consultant advisor.
    The user is asking a question about the current catalog of land plots. Answer the question thoroughly and contextually using ONLY the provided catalog data.
    
    Land Catalog:
    {"\n".join(plots_context)}
    
    User Question: {question}
    
    Provide your answer in clean Markdown format. Focus on being concise, professional, and helpful.
    """

    try:
        response = genai_client = get_genai_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        answer = response.text
    except Exception as e:
        raise Exception(f"AI advice generation failed: {str(e)}")

    if answer is None:
        raise Exception("AI advice generation returned no text")
    return answer
