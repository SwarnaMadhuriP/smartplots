from __future__ import annotations

from sqlalchemy import cast
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector

from app.models import Plot, PlotEmbedding
from app.rag.embeddings import generate_embedding


def build_plot_searchable_text(plot: Plot) -> str:
    """Build plot-only text for semantic search embeddings.

    Uploaded document contents are intentionally excluded. Documents are used by
    AI Advisor RAG, not by plot search embeddings.
    """
    utilities = [
        "road access available" if plot.road_access else "no road access",
        "water access available" if plot.water_access else "no water access",
        "electricity available" if plot.electricity else "no electricity",
        "sewer available" if plot.sewer else "no sewer",
    ]

    insight = plot.insight
    insight_parts: list[str] = []
    if insight:
        if insight.summary:
            insight_parts.append(f"Insight summary: {insight.summary}")
        if insight.investment_score is not None:
            insight_parts.append(f"Investment score: {insight.investment_score}")
        if insight.growth_potential:
            insight_parts.append(f"Growth potential: {insight.growth_potential}")
        if insight.risk_level:
            insight_parts.append(f"Risk level: {insight.risk_level}")
        for field_name in ("appreciation_potential", "pros", "cons"):
            value = getattr(insight, field_name, None)
            if value:
                insight_parts.append(f"{field_name.replace('_', ' ').title()}: {value}")

    parts = [
        f"Title: {plot.title}",
        f"Description: {plot.description or ''}",
        f"Location: {plot.city}, {plot.state} {plot.zip_code or ''}",
        f"Price: ${plot.price:,.0f}",
        f"Acreage: {plot.area_acres} acres",
        f"Zoning: {plot.zoning_type or 'General'}",
        f"Listing type: {plot.listing_type or 'sale'}",
        f"Status: {plot.status or 'available'}",
        f"Utilities: {', '.join(utilities)}",
        f"Nearby landmarks: {plot.nearby_landmarks or ''}",
        f"Ideal for: {plot.ideal_for or ''}",
        f"Risk notes: {plot.risk_notes or ''}",
        *insight_parts,
    ]
    return "\n".join(part for part in parts if part.strip())


def upsert_plot_embedding(db: Session, plot: Plot) -> PlotEmbedding:
    searchable_text = build_plot_searchable_text(plot)
    embedding_vector = generate_embedding(searchable_text)
    existing = (
        db.query(PlotEmbedding)
        .filter(PlotEmbedding.plot_id == plot.id)
        .one_or_none()
    )

    if existing:
        existing.searchable_text = searchable_text
        existing.embedding = embedding_vector
        return existing

    created = PlotEmbedding(
        plot_id=plot.id,
        searchable_text=searchable_text,
        embedding=embedding_vector,
    )
    db.add(created)
    return created


def upsert_all_plot_embeddings(db: Session) -> int:
    plots = db.query(Plot).all()
    for plot in plots:
        upsert_plot_embedding(db, plot)
    db.commit()
    return len(plots)


def semantic_plot_ids(
    db: Session,
    query: str,
    limit: int = 25,
) -> list[int]:
    q_vector = generate_embedding(query)
    rows = (
        db.query(PlotEmbedding.plot_id)
        .order_by(PlotEmbedding.embedding.cosine_distance(cast(q_vector, Vector(768))))
        .limit(limit)
        .all()
    )
    return [int(row[0]) for row in rows]
