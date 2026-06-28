import json

from google.genai import types
from pydantic import BaseModel

from app.core.gemini import call_with_retry
from app.models import Plot


class MarketReport(BaseModel):
    market_overview: str
    top_picks: list[str]
    critical_risk_alerts: list[str]
    development_readiness_notes: str


class AdvisorOutput(BaseModel):
    """Structured output for the AI Advisor, used as Gemini response_schema."""

    answer: str
    cited_plot_ids: list[int]
    suggested_follow_ups: list[str]


def run_catalog_advice(plots: list[Plot], question: str) -> str:
    plots_context = []
    for plot in plots:
        plots_context.append(
            f"- Plot ID: {plot.id}, Title: {plot.title}, Price: ${plot.price}, "
            f"Area: {plot.area_acres} acres, City: {plot.city}, State: {plot.state}, "
            f"Zoning: {plot.zoning_type or 'General'}, Road Access: {plot.road_access}, "
            f"Water Access: {plot.water_access}, Electricity: {plot.electricity}, "
            f"Sewer: {plot.sewer}, Ideal For: {plot.ideal_for or 'N/A'}, "
            f"Risk Notes: {plot.risk_notes or 'None'}"
        )

    catalog = "\n".join(plots_context)
    prompt = f"""
You are an expert land consultant advisor.
The user is asking a question about the current catalog of land plots.
Answer the question thoroughly and contextually using ONLY the provided catalog data.

Land Catalog:
{catalog}

User Question: {question}

Provide your answer in clean Markdown format. Focus on being concise, professional, and helpful.
"""

    try:
        response = call_with_retry(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3),
        )
        answer = response.text
    except Exception as e:
        raise RuntimeError(f"AI advice generation failed: {e}") from e

    if answer is None:
        raise RuntimeError("AI advice generation returned no text")
    return answer


def run_advisor_response(
    question: str,
    plots: list[Plot],
    focus_plot: Plot | None = None,
) -> dict:
    """
    Answers a user question using plot data, optionally scoped to a single plot.
    """

    def plot_summary(plot: Plot) -> str:
        return (
            f"Plot ID:      {plot.id}\n"
            f"Title:        {plot.title}\n"
            f"Location:     {plot.city}, {plot.state}\n"
            f"Price:        ${plot.price:,}\n"
            f"Size:         {plot.area_acres} acres\n"
            f"Zoning:       {plot.zoning_type or 'General'}\n"
            f"Match Score:  {plot.computed_match_score}/10\n"
            f"Risk Level:   {plot.computed_risk_level}\n"
            f"Rental Demand:{plot.computed_rental_demand}\n"
            f"Road access:  {'Yes' if plot.road_access else 'No'}\n"
            f"Water access: {'Yes' if plot.water_access else 'No'}\n"
            f"Electricity:  {'Yes' if plot.electricity else 'No'}\n"
            f"Sewer:        {'Yes' if plot.sewer else 'No'}\n"
            f"Ideal for:    {plot.ideal_for or 'N/A'}\n"
            f"Risk notes:   {plot.risk_notes or 'N/A'}"
        )

    catalog_block = "\n\n".join(plot_summary(plot) for plot in plots)

    if focus_plot:
        scope_section = f"""\
You are advising on a specific plot. Answer the user's question about this plot,
using the full catalog below only for context and comparison.

Focus Plot:
{plot_summary(focus_plot)}

Full Catalog (for comparison context):
{catalog_block}
"""
    else:
        scope_section = f"""\
You are advising on the user's full land catalog. Answer based only on the plots below.

Full Catalog:
{catalog_block}
"""

    prompt = f"""\
You are an expert AI land advisor for SmartPlots. Your role is to help users
make informed decisions about land plots based strictly on the provided data.

{scope_section}

User question: {question}

Rules:
- Base your answer ONLY on the data provided above.
- Do not invent facts, prices, locations, or utilities not listed.
- Write your answer in clear, concise Markdown.
- In cited_plot_ids, list only the Plot IDs you directly referenced.
- In suggested_follow_ups, provide 2-3 natural follow-up questions the user might ask next.
"""

    try:
        response = call_with_retry(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AdvisorOutput,
                temperature=0.3,
            ),
        )

        if not response.text:
            raise ValueError("AI advisor returned empty response.")

        return json.loads(response.text)

    except Exception as e:
        raise RuntimeError(f"AI advisor failed: {e}") from e
