from typing import TypedDict
from .database import SessionLocal
from .models import Plot, PlotImage, Document, DocumentChunk
from sqlalchemy import text
from app.rag.ingest import ingest_document

db = SessionLocal()

# plot = Plot(
#     title="Green Valley Plot",
#     description="Great residential land near highway",
#     price=85000,
#     area_acres=0.75,
#     city="Austin",
#     state="TX",
#     zoning_type="residential",
#     road_access=True,
#     water_access=True,
#     electricity=True
# )

plots = [
    Plot(
        title="Green Valley Residential Plot",
        description="Ideal residential plot near growing suburbs.",
        price=85000,
        area_acres=0.75,
        city="Austin",
        state="TX",
        latitude=30.2672,
        longitude=-97.7431,
        zoning_type="residential",
        road_access=True,
        water_access=True,
        electricity=True,
        nearby_landmarks="10 mins from downtown, near Highway 45",
        ideal_for="Residential home, long-term investment",
        risk_notes="Check soil quality before construction",
    ),
    Plot(
        title="Lakeside Retreat Land",
        description="Scenic plot near lake, perfect for vacation home.",
        price=120000,
        area_acres=1.2,
        city="Austin",
        state="TX",
        latitude=30.3935,
        longitude=-97.9111,
        zoning_type="residential",
        road_access=True,
        water_access=True,
        electricity=False,
        nearby_landmarks="Near Lake Travis",
        ideal_for="Vacation home, Airbnb",
        risk_notes="Limited electricity access",
    ),
    Plot(
        title="Downtown Investment Lot",
        description="Prime location for commercial investment.",
        price=250000,
        area_acres=0.5,
        city="Dallas",
        state="TX",
        latitude=32.7767,
        longitude=-96.7970,
        zoning_type="commercial",
        road_access=True,
        water_access=True,
        electricity=True,
        nearby_landmarks="Central Dallas business district",
        ideal_for="Commercial buildings",
        risk_notes="High competition and cost",
    ),
    Plot(
        title="Farmland Opportunity",
        description="Large agricultural land for farming.",
        price=60000,
        area_acres=3.5,
        city="Waco",
        state="TX",
        latitude=31.5493,
        longitude=-97.1467,
        zoning_type="agricultural",
        road_access=True,
        water_access=False,
        electricity=False,
        nearby_landmarks="Rural farming area",
        ideal_for="Farming, long-term land holding",
        risk_notes="Limited water supply",
    ),
    Plot(
        title="Suburban Growth Plot",
        description="Located in rapidly growing suburb.",
        price=95000,
        area_acres=0.9,
        city="Houston",
        state="TX",
        latitude=29.7604,
        longitude=-95.3698,
        zoning_type="residential",
        road_access=True,
        water_access=True,
        electricity=True,
        nearby_landmarks="New schools and shopping centers nearby",
        ideal_for="Family home",
        risk_notes="Area still under development",
    ),
    Plot(
        title="Highway Commercial Lot",
        description="Perfect for retail or gas station.",
        price=180000,
        area_acres=1.0,
        city="San Antonio",
        state="TX",
        latitude=29.4241,
        longitude=-98.4936,
        zoning_type="commercial",
        road_access=True,
        water_access=True,
        electricity=True,
        nearby_landmarks="Direct highway frontage",
        ideal_for="Retail, business",
        risk_notes="Traffic noise",
    ),
    Plot(
        title="Budget Starter Plot",
        description="Affordable entry-level land for first-time buyers.",
        price=45000,
        area_acres=0.6,
        city="Waco",
        state="TX",
        latitude=31.5000,
        longitude=-97.2000,
        zoning_type="residential",
        road_access=False,
        water_access=False,
        electricity=False,
        nearby_landmarks="10 mins from town",
        ideal_for="Budget buyers",
        risk_notes="No utilities yet",
    ),
    Plot(
        title="Luxury Estate Land",
        description="Premium land for luxury estate development.",
        price=320000,
        area_acres=2.5,
        city="Austin",
        state="TX",
        latitude=30.3072,
        longitude=-97.9000,
        zoning_type="residential",
        road_access=True,
        water_access=True,
        electricity=True,
        nearby_landmarks="Gated community, hilltop views",
        ideal_for="Luxury villa",
        risk_notes="High initial investment",
    ),
]

db.query(PlotImage).delete()
db.query(DocumentChunk).delete()
db.query(Document).delete()
db.query(Plot).delete()
db.commit()

db.execute(text("ALTER SEQUENCE plots_id_seq RESTART WITH 1"))
db.execute(text("ALTER SEQUENCE plot_images_id_seq RESTART WITH 1"))
db.execute(text("ALTER SEQUENCE documents_id_seq RESTART WITH 1"))
db.execute(text("ALTER SEQUENCE document_chunks_id_seq RESTART WITH 1"))
db.commit()

db.add_all(plots)
db.commit()

images = [
    PlotImage(
        plot_id=1,
        image_url="https://images.unsplash.com/photo-1500382017468-9049fed747ef",
        alt_text="Open green land",
        is_primary=True,
    ),
    PlotImage(
        plot_id=2,
        image_url="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
        alt_text="Lakeside land",
        is_primary=True,
    ),
    PlotImage(
        plot_id=3,
        image_url="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab",
        alt_text="Commercial area",
        is_primary=True,
    ),
    PlotImage(
        plot_id=4,
        image_url="https://images.unsplash.com/photo-1464226184884-fa280b87c399",
        alt_text="Farmland",
        is_primary=True,
    ),
    PlotImage(
        plot_id=5,
        image_url="https://images.unsplash.com/photo-1448630360428-65456885c650",
        alt_text="Suburban land",
        is_primary=True,
    ),
    PlotImage(
        plot_id=6,
        image_url="https://images.unsplash.com/photo-1494526585095-c41746248156",
        alt_text="Highway land",
        is_primary=True,
    ),
    PlotImage(
        plot_id=7,
        image_url="https://images.unsplash.com/photo-1500382017468-9049fed747ef",
        alt_text="Budget starter land",
        is_primary=True,
    ),
    PlotImage(
        plot_id=8,
        image_url="https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
        alt_text="Luxury estate land",
        is_primary=True,
    ),
]

db.add_all(images)
db.commit()

class DocToIngest(TypedDict):
    file_path: str
    plot_id: int
    document_type: str

# Ingest real uploaded documents for plot 1 and plot 2
docs_to_ingest: list[DocToIngest] = [
    # Plot 1 — Green Valley Residential Plot
    {
        "file_path": "uploads/documents/plot-1/brochure.pdf",
        "plot_id": 1,
        "document_type": "brochure",
    },
    {
        "file_path": "uploads/documents/plot-1/investment_report.pdf",
        "plot_id": 1,
        "document_type": "investment_report",
    },
    {
        "file_path": "uploads/documents/plot-1/property_fact_sheet.pdf",
        "plot_id": 1,
        "document_type": "property_fact_sheet",
    },
    {
        "file_path": "uploads/documents/plot-1/zoning_report.pdf",
        "plot_id": 1,
        "document_type": "zoning_report",
    },
    {
        "file_path": "uploads/documents/plot-1/soil_report.pdf",
        "plot_id": 1,
        "document_type": "soil_report",
    },
    {
        "file_path": "uploads/documents/plot-1/utility_report.pdf",
        "plot_id": 1,
        "document_type": "utility_report",
    },
    {
        "file_path": "uploads/documents/plot-1/neighborhood_guide.pdf",
        "plot_id": 1,
        "document_type": "neighborhood_guide",
    },
    {
        "file_path": "uploads/documents/plot-1/property_disclosure.pdf",
        "plot_id": 1,
        "document_type": "property_disclosure",
    },
    {
        "file_path": "uploads/documents/plot-1/county_growth_report.pdf",
        "plot_id": 1,
        "document_type": "county_growth_report",
    },
    {
        "file_path": "uploads/documents/plot-1/due_diligence_checklist.pdf",
        "plot_id": 1,
        "document_type": "due_diligence_checklist",
    },
    # Plot 2 — Lakeside Retreat Land
    {
        "file_path": "uploads/documents/plot-2/brochure.pdf",
        "plot_id": 2,
        "document_type": "brochure",
    },
    {
        "file_path": "uploads/documents/plot-2/property_fact_sheet.pdf",
        "plot_id": 2,
        "document_type": "property_fact_sheet",
    },
    {
        "file_path": "uploads/documents/plot-2/zoning_report.pdf",
        "plot_id": 2,
        "document_type": "zoning_report",
    },
    {
        "file_path": "uploads/documents/plot-2/soil_report.pdf",
        "plot_id": 2,
        "document_type": "soil_report",
    },
    {
        "file_path": "uploads/documents/plot-2/utility_report.pdf",
        "plot_id": 2,
        "document_type": "utility_report",
    },
    {
        "file_path": "uploads/documents/plot-2/neighborhood_guide.pdf",
        "plot_id": 2,
        "document_type": "neighborhood_guide",
    },
    {
        "file_path": "uploads/documents/plot-2/property_disclosure.pdf",
        "plot_id": 2,
        "document_type": "property_disclosure",
    },
    {
        "file_path": "uploads/documents/plot-2/county_growth_report.pdf",
        "plot_id": 2,
        "document_type": "county_growth_report",
    },
    {
        "file_path": "uploads/documents/plot-2/due_diligence_checklist.pdf",
        "plot_id": 2,
        "document_type": "due_diligence_checklist",
    },
]

print("Ingesting real plot documents for RAG...")
for doc in docs_to_ingest:
    print(f"  Ingesting {doc['file_path']}...")
    ingest_document(
        db=db,
        file_path=doc["file_path"],
        plot_id=doc["plot_id"],
        document_type=doc["document_type"],
    )
print(f"Done. Ingested {len(docs_to_ingest)} documents.")

db.close()
