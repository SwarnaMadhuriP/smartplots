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


def retrieve_plot_context(
    plot_ids: list[int],
    query: str,
    db: Session,
    limit_per_plot: int = 3,
) -> list[dict]:
    """
    Retrieve relevant document chunks for a scored plot shortlist.

    This reuses the existing pgvector-backed document_chunks table and Gemini
    embedding helper. Results are grouped by plot by issuing a bounded query per
    plot, which keeps each shortlisted plot represented without letting one
    document-heavy plot consume the whole context window.
    """
    if not plot_ids:
        return []

    q_vector = generate_embedding(query)
    results: list[dict] = []

    for plot_id in plot_ids:
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.plot_id == plot_id)
            .order_by(
                DocumentChunk.embedding.cosine_distance(
                    cast(q_vector, Vector(768))
                )
            )
            .limit(limit_per_plot)
            .all()
        )

        for chunk in chunks:
            document = chunk.document
            results.append(
                {
                    "plot_id": plot_id,
                    "document_type": document.document_type if document else "document",
                    "filename": document.filename if document else "unknown",
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.chunk_text,
                }
            )

    return results
