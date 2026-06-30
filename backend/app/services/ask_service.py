import json
from typing import Any, cast as type_cast

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.prompts import ASK_SMARTPLOTS_PROMPT
from app.core.genai_client import get_genai_client
from app.models import DocumentChunk, Plot
from app.services.routing_service import QuestionRoute, classify_question, select_ask_specialists
from app.tools.analysis_tools import (
    calculate_investment_metrics,
    calculate_location_metrics,
    calculate_risk_metrics,
)


def _property_context(plot: Plot) -> dict[str, Any]:
    return {
        "id": plot.id,
        "title": plot.title,
        "description": plot.description,
        "location": f"{plot.city}, {plot.state}",
        "price": plot.price,
        "area_acres": plot.area_acres,
        "zoning_type": plot.zoning_type,
        "utilities": {
            "road_access": plot.road_access,
            "water_access": plot.water_access,
            "electricity": plot.electricity,
            "sewer": plot.sewer,
        },
        "nearby_landmarks": plot.nearby_landmarks,
        "ideal_for": plot.ideal_for,
        "risk_notes": plot.risk_notes,
    }


def _run_ask_specialists(
    plot: Plot,
    question: str,
    specialists: list[QuestionRoute],
) -> dict[str, Any]:
    analysis: dict[str, Any] = {}
    purpose = question if QuestionRoute.LOCATION in specialists else None

    for specialist in specialists:
        if specialist == QuestionRoute.INVESTMENT:
            analysis["investment"] = calculate_investment_metrics(plot)
        elif specialist == QuestionRoute.RISK:
            analysis["risk"] = calculate_risk_metrics(plot)
        elif specialist == QuestionRoute.LOCATION:
            analysis["location"] = calculate_location_metrics(plot, purpose=purpose)

    return analysis


def _source_references(chunks: list[DocumentChunk]) -> list[dict[str, Any]]:
    sources = []
    seen = set()
    for chunk in chunks:
        filename = chunk.document.filename if chunk.document else "unknown"
        document_type = chunk.document.document_type if chunk.document else "document"
        key = (filename, chunk.page_number)

        if key in seen:
            continue

        seen.add(key)
        text = type_cast(str, chunk.chunk_text) if chunk.chunk_text else ""
        excerpt = text[:200] + "..." if len(text) > 200 else text
        sources.append(
            {
                "filename": filename,
                "page": chunk.page_number,
                "excerpt": excerpt,
                "document_type": document_type,
            }
        )

    return sources


def _document_context_from_chunks(chunks: list[DocumentChunk]) -> str:
    if not chunks:
        return "No uploaded document evidence was retrieved for this question."

    context_parts = []
    for chunk in chunks:
        filename = chunk.document.filename if chunk.document else "unknown"
        page = f" (page {chunk.page_number})" if chunk.page_number else ""
        context_parts.append(f"[{filename}{page}]\n{chunk.chunk_text}")
    return "\n\n---\n\n".join(context_parts)


def _retrieve_document_evidence(
    plot_id: int,
    question: str,
    db: Session,
) -> list[DocumentChunk]:
    from google.genai import types
    from pgvector.sqlalchemy import Vector
    from sqlalchemy import cast

    try:
        embed_response = get_genai_client().models.embed_content(
            model="gemini-embedding-2",
            contents=question,
            config=types.EmbedContentConfig(output_dimensionality=768),
        )
    except Exception:
        return []

    if not embed_response.embeddings:
        return []

    q_vector = embed_response.embeddings[0].values
    try:
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.plot_id == plot_id)
            .order_by(
                DocumentChunk.embedding.cosine_distance(cast(q_vector, Vector(768)))
            )
            .limit(5)
            .all()
        )
    except Exception:
        return []


def _compose_ask_answer(
    question: str,
    route: QuestionRoute,
    plot: Plot,
    chunks: list[DocumentChunk],
    specialists: list[QuestionRoute],
    specialist_analysis: dict[str, Any],
) -> str:
    from google.genai import types

    prompt = ASK_SMARTPLOTS_PROMPT.format(
        question=question,
        route=route.value,
        selected_specialists=json.dumps(
            [specialist.value for specialist in specialists],
            indent=2,
        ),
        property_context=json.dumps(_property_context(plot), indent=2),
        document_context=_document_context_from_chunks(chunks),
        specialist_context=json.dumps(specialist_analysis, indent=2),
    )

    try:
        response = get_genai_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1),
        )
        return response.text or "No answer generated."
    except Exception as e:
        err = str(e).lower()
        if any(k in err for k in ("quota", "rate", "429", "resource exhausted", "exhausted")):
            raise HTTPException(status_code=429, detail="Rate limit reached. Please wait a moment and try again.")
        raise HTTPException(status_code=500, detail=str(e))


def ask_about_plot(plot: Plot, question: str, db: Session) -> dict[str, Any]:
    question_route = classify_question(question)
    chunks = _retrieve_document_evidence(type_cast(int, plot.id), question, db)
    specialists = select_ask_specialists(question)
    specialist_analysis = _run_ask_specialists(plot, question, specialists)
    answer = _compose_ask_answer(
        question=question,
        route=question_route,
        plot=plot,
        chunks=chunks,
        specialists=specialists,
        specialist_analysis=specialist_analysis,
    )

    missing_fields = [
        f for f in ["zoning_type", "risk_notes", "sewer"]
        if not getattr(plot, f, None)
    ]

    plot_context = {
        "price": plot.price,
        "area_acres": plot.area_acres,
        "zoning_type": plot.zoning_type,
        "city": plot.city,
        "state": plot.state,
        "road_access": plot.road_access,
        "water_access": plot.water_access,
        "electricity": plot.electricity,
        "sewer": plot.sewer,
        "nearby_landmarks": plot.nearby_landmarks,
        "risk_notes": plot.risk_notes,
    }

    return {
        "answer": answer,
        "sources": _source_references(chunks),
        "has_documents": bool(chunks),
        "route": question_route.value,
        "specialists": [specialist.value for specialist in specialists],
        "missing_fields": missing_fields,
        "plot_context": plot_context,
    }
