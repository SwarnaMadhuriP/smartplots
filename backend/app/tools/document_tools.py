from app.core.genai_client import get_genai_client
from app.database import SessionLocal
from app.models import DocumentChunk
from app.agents.context import ToolContext


def retrieve_plot_documents(
    plot_id: int,
    question: str,
    tool_context: ToolContext | None = None,
) -> list[dict]:
    """Retrieves document chunks relevant to a specific plot and question.

    Args:
        plot_id: The database ID of the plot.
        question: The user query or question to search documents for.

    Returns:
        A list of dicts with document_type, filename, page_number, and text.
    """
    db = SessionLocal()
    try:
        from google.genai import types

        client = get_genai_client()
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=question,
            config=types.EmbedContentConfig(output_dimensionality=768),
        )
        if response.embeddings and len(response.embeddings) > 0:
            question_embedding = response.embeddings[0].values
        elif (
            hasattr(response, "embedding")
            and getattr(response, "embedding") is not None
        ):
            question_embedding = getattr(response, "embedding").values
        else:
            raise ValueError(
                f"Failed to generate embedding: embeddings list is empty or None in response. Response was: {response}"
            )

        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.plot_id == plot_id)
            .order_by(DocumentChunk.embedding.cosine_distance(question_embedding))
            .limit(5)
            .all()
        )

        results = []
        for chunk in chunks:
            results.append(
                {
                    "document_type": chunk.document.document_type,
                    "filename": chunk.document.filename,
                    "page_number": chunk.page_number,
                    "text": chunk.chunk_text,
                }
            )
        return results
    finally:
        db.close()
