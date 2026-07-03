from pathlib import Path
from typing import Iterable

from sqlalchemy import text

from app.database import SessionLocal
from app.models import Document, DocumentChunk, Plot
from app.rag.ingest import ingest_document


DOCUMENTS_ROOT = Path("uploads/documents")
SUPPORTED_EXTENSIONS = {".pdf"}


def infer_document_type(file_path: Path) -> str:
    """Convert filenames like zoning_report.pdf -> zoning_report."""
    return file_path.stem.lower().replace(" ", "_").replace("-", "_")


def iter_plot_document_files(documents_root: Path) -> Iterable[tuple[int, Path]]:
    """
    Reads folders like:
      uploads/documents/plot-1/brochure.pdf
      uploads/documents/plot-2/zoning_report.pdf

    Returns:
      (plot_id, file_path)
    """
    if not documents_root.exists():
        print(f"Documents folder not found: {documents_root}")
        return

    for plot_dir in sorted(documents_root.glob("plot-*")):
        if not plot_dir.is_dir():
            continue

        try:
            plot_id = int(plot_dir.name.replace("plot-", ""))
        except ValueError:
            print(f"Skipping invalid plot folder: {plot_dir}")
            continue

        for file_path in sorted(plot_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield plot_id, file_path


def clear_existing_document_data(db) -> None:
    """Only clears RAG/document tables. Does not touch plots or plot_images."""
    db.query(DocumentChunk).delete()
    db.query(Document).delete()
    db.commit()

    # Optional sequence reset for Postgres. Safe to remove if using SQLite.
    try:
        db.execute(text("ALTER SEQUENCE documents_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE document_chunks_id_seq RESTART WITH 1"))
        db.commit()
    except Exception:
        db.rollback()


def main() -> None:
    db = SessionLocal()

    try:
        clear_existing_document_data(db)

        ingested_count = 0
        skipped_count = 0

        print(f"Scanning documents under: {DOCUMENTS_ROOT}")

        for plot_id, file_path in iter_plot_document_files(DOCUMENTS_ROOT):
            plot_exists = db.query(Plot.id).filter(Plot.id == plot_id).first()
            if not plot_exists:
                print(f"Skipping {file_path}: plot_id={plot_id} does not exist")
                skipped_count += 1
                continue

            document_type = infer_document_type(file_path)
            print(f"Ingesting plot {plot_id}: {file_path} as {document_type}")

            ingest_document(
                db=db,
                file_path=str(file_path),
                plot_id=plot_id,
                document_type=document_type,
            )
            ingested_count += 1

        print("Document ingestion complete.")
        print(f"Ingested: {ingested_count}")
        print(f"Skipped: {skipped_count}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
