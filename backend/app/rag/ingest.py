import os

from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.rag.chunking import chunk_text
from app.rag.embeddings import generate_embedding
from app.rag.extract import extract_text_from_file


def ingest_document(
    db: Session,
    file_path: str,
    plot_id: int,
    document_type: str,
) -> Document:
    pages = extract_text_from_file(file_path)

    db_doc = Document(
        plot_id=plot_id,
        document_type=document_type,
        filename=os.path.basename(file_path),
        file_path=file_path,
    )
    db.add(db_doc)
    db.flush()

    chunk_index = 0

    for page_num, text_content in pages:
        chunks = chunk_text(text_content, page_num)

        for chunk in chunks:
            chunk_txt = chunk["text"]
            embedding_vector = generate_embedding(chunk_txt)

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