from sqlalchemy.orm import Session
from sqlalchemy import cast
from pgvector.sqlalchemy import Vector

from app.models import DocumentChunk
from app.rag.embeddings import generate_embedding


def retrieve_document_evidence(
    plot_id: int,
    question: str,
    db: Session,
    limit: int = 5,
) -> list[DocumentChunk]:
    q_vector = generate_embedding(question)

    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.plot_id == plot_id)
        .order_by(
            DocumentChunk.embedding.cosine_distance(
                cast(q_vector, Vector(768))
            )
        )
        .limit(limit)
        .all()
    )