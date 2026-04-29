from .database import SessionLocal
from .models import Plot, PlotImage

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
        zoning_type="residential",
        road_access=True,
        water_access=True,
        electricity=True,
        nearby_landmarks="Gated community, hilltop views",
        ideal_for="Luxury villa",
        risk_notes="High initial investment",
    ),
]
if db.query(Plot).count() == 0:
    db.add_all(plots)
    db.commit()

# Clear images before re-adding (prevents duplicates)
db.query(PlotImage).delete()
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

# db.add(plot)
# db.commit()
db.close()
