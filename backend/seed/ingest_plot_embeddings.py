from app.database import SessionLocal
from app.services.plot_embedding_service import upsert_all_plot_embeddings


def main() -> None:
    db = SessionLocal()
    try:
        count = upsert_all_plot_embeddings(db)
        print(f"Upserted plot embeddings for {count} plot(s).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
