import os
import pypdf
from sqlalchemy.orm import Session
from app.models import Document, DocumentChunk
from app.portfolio_agents import get_genai_client


def extract_text_from_file(file_path: str) -> list[tuple[int, str]]:
    """Extracts text from PDF or text file.
    Returns a list of tuples: (page_number, text_content)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        pages = []
        try:
            reader = pypdf.PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append((idx + 1, text))
        except Exception as e:
            # Fallback to empty text if corrupted
            print(f"Error reading PDF {file_path}: {e}")
        return pages
    else:
        # Assume plain text file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return [(1, text)]


def chunk_text(
    text: str, page_number: int, chunk_size: int = 800, overlap: int = 150
) -> list[dict]:
    """Splits text into chunks using a character-based sliding window."""
    chunks = []
    text = text.strip()
    if not text:
        return chunks

    start = 0
    chunk_idx = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk_text = text[start:end]
        chunks.append(
            {"text": chunk_text, "page_number": page_number, "chunk_index": chunk_idx}
        )
        chunk_idx += 1
        start += chunk_size - overlap
        if start >= text_len or end == text_len:
            break

    return chunks


def ingest_document(
    db: Session, file_path: str, plot_id: int, document_type: str
) -> Document:
    """Ingests a document, extracts text, chunks it, generates embeddings, and saves to database."""
    # Extract text by page
    pages = extract_text_from_file(file_path)

    # Save document entry
    db_doc = Document(
        plot_id=plot_id,
        document_type=document_type,
        filename=os.path.basename(file_path),
        file_path=file_path,
    )
    db.add(db_doc)
    db.flush()  # Populates db_doc.id

    client = get_genai_client()

    chunk_index = 0
    for page_num, text_content in pages:
        chunks = chunk_text(text_content, page_num)
        for chunk in chunks:
            chunk_txt = chunk["text"]

            # Generate embedding
            from google.genai import types

            response = client.models.embed_content(
                model="gemini-embedding-2",
                contents=chunk_txt,
                config=types.EmbedContentConfig(output_dimensionality=768),
            )
            if response.embeddings and len(response.embeddings) > 0:
                embedding_vector = response.embeddings[0].values
            elif (
                hasattr(response, "embedding")
                and getattr(response, "embedding") is not None
            ):
                embedding_vector = getattr(response, "embedding").values
            else:
                raise ValueError(
                    f"Failed to generate embedding: embeddings list is empty or None in response. Response was: {response}"
                )

            db_chunk = DocumentChunk(
                document_id=db_doc.id,
                plot_id=plot_id,
                chunk_text=chunk_txt,
                embedding=embedding_vector,
                page_number=page_num,
                chunk_index=chunk_index,
            )
            db.add(db_chunk)
            chunk_index += 1

    db.commit()
    return db_doc
