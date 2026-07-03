from sqlalchemy import text

from app.database import SessionLocal
from app.models import Plot, PlotImage, Document, DocumentChunk


def reset_demo_data(db) -> None:
    """Clear demo tables once before seeding all states."""
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


def add_plots_with_images(db, plots: list[Plot], image_data: list[dict]) -> None:
    """
    Add plots and their primary images without hardcoding plot IDs.

    image_data must be in the same order as plots.
    """
    if len(plots) != len(image_data):
        raise ValueError("plots and image_data must have the same length")

    db.add_all(plots)
    db.commit()

    images = [
        PlotImage(
            plot_id=plot.id,
            image_url=image["image_url"],
            alt_text=image["alt_text"],
            is_primary=image.get("is_primary", True),
        )
        for plot, image in zip(plots, image_data)
    ]

    db.add_all(images)
    db.commit()


def seed_california(db) -> None:
    plots = [
        Plot(
            title="San Jose Tech Corridor Residential Lot",
            description=(
                "Build-ready residential land near major Silicon Valley employers. "
                "Strong fit for custom home buyers and long-term appreciation."
            ),
            price=425000,
            area_acres=0.42,
            city="San Jose",
            state="CA",
            zip_code="95134",
            latitude=37.4111,
            longitude=-121.9411,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Apple Park, NVIDIA campus, Santana Row, San Jose International Airport",
            ideal_for="Build a Home, Invest for Appreciation",
            risk_notes="Premium pricing due to strong Silicon Valley demand.",
        ),
        Plot(
            title="Sacramento Family Build Lot",
            description=(
                "Affordable California residential parcel with utilities and paved access. "
                "Designed for family-home searches and value-focused buyers."
            ),
            price=165000,
            area_acres=0.65,
            city="Sacramento",
            state="CA",
            zip_code="95829",
            latitude=38.4755,
            longitude=-121.3418,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Elk Grove schools, neighborhood parks, grocery centers, downtown Sacramento",
            ideal_for="Build a Home, Maximize Value",
            risk_notes="Moderate appreciation compared with coastal California markets.",
        ),
        Plot(
            title="Napa Valley Vineyard Estate Parcel",
            description=(
                "Scenic wine-country land suited for a luxury retreat, vineyard concept, "
                "or retirement lifestyle property."
            ),
            price=690000,
            area_acres=2.8,
            city="Napa",
            state="CA",
            zip_code="94558",
            latitude=38.5025,
            longitude=-122.2654,
            zoning_type="agricultural",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=False,
            nearby_landmarks="Napa wineries, Silverado Trail, luxury resorts, fine dining",
            ideal_for="Retirement / Lifestyle, Invest for Appreciation",
            risk_notes="Septic planning and agricultural use restrictions may apply.",
        ),
        Plot(
            title="South Lake Tahoe Cabin Retreat Land",
            description=(
                "Mountain-view parcel near Lake Tahoe recreation areas. Good fit for a "
                "vacation cabin, lifestyle retreat, or long-term recreational holding."
            ),
            price=310000,
            area_acres=0.9,
            city="South Lake Tahoe",
            state="CA",
            zip_code="96150",
            latitude=38.9399,
            longitude=-119.9772,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=False,
            nearby_landmarks="Lake Tahoe beaches, Heavenly Ski Resort, Emerald Bay State Park",
            ideal_for="Retirement / Lifestyle, Invest for Appreciation",
            risk_notes="Snow access and seasonal construction constraints should be reviewed.",
        ),
        Plot(
            title="Palm Springs Desert Lifestyle Lot",
            description=(
                "Sunny desert parcel near resorts and golf communities. Strong demo fit for "
                "retirement, vacation use, and lifestyle searches."
            ),
            price=220000,
            area_acres=0.75,
            city="Palm Springs",
            state="CA",
            zip_code="92262",
            latitude=33.8303,
            longitude=-116.5453,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Palm Springs resorts, golf courses, Joshua Tree, downtown Palm Springs",
            ideal_for="Retirement / Lifestyle, Maximize Value",
            risk_notes="Extreme summer heat and water usage should be considered.",
        ),
        Plot(
            title="Monterey Coastal View Parcel",
            description=(
                "Premium coastal-area parcel near Monterey attractions. Suitable for a scenic "
                "custom home or lifestyle investment."
            ),
            price=540000,
            area_acres=0.55,
            city="Monterey",
            state="CA",
            zip_code="93940",
            latitude=36.6002,
            longitude=-121.8947,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Monterey Bay Aquarium, Carmel-by-the-Sea, Pebble Beach, Pacific Coast Highway",
            ideal_for="Retirement / Lifestyle, Build a Home",
            risk_notes="Coastal permitting and design restrictions may increase development complexity.",
        ),
        Plot(
            title="Yosemite Gateway Recreation Land",
            description=(
                "Rural recreation parcel positioned near Yosemite access routes. Ideal for "
                "cabin, camping, or nature-focused ownership."
            ),
            price=185000,
            area_acres=3.2,
            city="Mariposa",
            state="CA",
            zip_code="95338",
            latitude=37.4849,
            longitude=-119.9663,
            zoning_type="rural residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=False,
            electricity=True,
            sewer=False,
            nearby_landmarks="Yosemite National Park, Merced River, hiking trails, Mariposa town center",
            ideal_for="Retirement / Lifestyle, Maximize Value",
            risk_notes="Water access and septic feasibility need verification.",
        ),
        Plot(
            title="San Diego Coastal Lifestyle Lot",
            description=(
                "High-demand Southern California parcel near beaches, parks, and healthcare. "
                "Strong match for lifestyle buyers and premium home construction."
            ),
            price=615000,
            area_acres=0.38,
            city="San Diego",
            state="CA",
            zip_code="92130",
            latitude=32.9595,
            longitude=-117.2653,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="La Jolla, Torrey Pines, UC San Diego, beaches, hospitals",
            ideal_for="Build a Home, Retirement / Lifestyle",
            risk_notes="Premium location with higher property taxes and build costs.",
        ),
        Plot(
            title="Santa Cruz Mountain View Lot",
            description=(
                "Scenic parcel near redwoods and coastal attractions. Good fit for peaceful "
                "living, a weekend retreat, or a custom home search."
            ),
            price=375000,
            area_acres=1.1,
            city="Santa Cruz",
            state="CA",
            zip_code="95060",
            latitude=37.0105,
            longitude=-122.0647,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=False,
            nearby_landmarks="Santa Cruz Beach Boardwalk, redwood parks, Pacific Coast Highway",
            ideal_for="Retirement / Lifestyle, Build a Home",
            risk_notes="Slope and wildfire risk should be reviewed before development.",
        ),
        Plot(
            title="Anaheim Tourism Commercial Parcel",
            description=(
                "Commercial-zoned lot near major tourism corridors. Suitable for retail, "
                "parking, or hospitality-adjacent use."
            ),
            price=780000,
            area_acres=0.7,
            city="Anaheim",
            state="CA",
            zip_code="92802",
            latitude=33.8038,
            longitude=-117.9152,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Disneyland, Anaheim Convention Center, hotels, restaurants",
            ideal_for="Commercial Development, Invest for Appreciation",
            risk_notes="High competition and permitting requirements for commercial development.",
        ),
    ]

    image_data = [
        {
            "image_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Buildable suburban residential lot near a Silicon Valley neighborhood",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Flat suburban residential lot suitable for a Sacramento family home",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Vineyard land suitable for a Napa Valley estate parcel",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Wooded mountain land suitable for a Lake Tahoe cabin site",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Desert residential land near Palm Springs resort communities",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Coastal California land suitable for a Monterey custom home",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Forest recreation land near Yosemite access routes",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Coastal Southern California homesite land near San Diego",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Wooded Santa Cruz mountain parcel with redwood character",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Commercial development parcel near a tourism corridor",
            "is_primary": True,
        },
    ]

    add_plots_with_images(db, plots, image_data)
    print(f"Seeded {len(plots)} California plots.")


def seed_washington(db) -> None:
    plots = [
        Plot(
            title="Queen Anne Infill Lot With Lake Union Outlook",
            description=(
                "Rare close-in Seattle residential parcel on a quiet Queen Anne side "
                "street, positioned for a modern single-family build or high-end DADU "
                "strategy. The site offers strong curb appeal, established neighborhood "
                "context, and quick access to South Lake Union employment centers."
            ),
            price=875000,
            area_acres=0.13,
            city="Seattle",
            state="WA",
            zip_code="98109",
            latitude=47.6376,
            longitude=-122.3567,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Lake Union, Space Needle, Amazon HQ, Seattle Center, Pike Place Market",
            ideal_for="Build a Home, Invest for Appreciation",
            risk_notes="Tight urban infill site may require careful survey, tree review, and construction staging planning.",
        ),
        Plot(
            title="Ballard Corner Lot Near Market Street",
            description=(
                "Flat Seattle infill lot in a walkable Ballard pocket with alley access "
                "and strong resale fundamentals. Suitable for a custom home, townhouse "
                "feasibility review, or long-term hold near transit, dining, and "
                "waterfront amenities."
            ),
            price=795000,
            area_acres=0.16,
            city="Seattle",
            state="WA",
            zip_code="98107",
            latitude=47.6688,
            longitude=-122.3824,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Seattle Waterfront, Pike Place Market, Lake Union, Ballard Locks, Space Needle",
            ideal_for="Maximize Value, Build a Home",
            risk_notes="Buyer should verify allowable density, parking requirements, and any utility relocation costs.",
        ),
        Plot(
            title="SoDo Commercial Pad With Downtown Visibility",
            description=(
                "Commercial-zoned Seattle parcel with excellent arterial exposure and "
                "access to downtown, port logistics, and stadium traffic. Strong "
                "candidate for boutique retail, service commercial, contractor yard, "
                "or future assemblage strategy."
            ),
            price=1850000,
            area_acres=0.34,
            city="Seattle",
            state="WA",
            zip_code="98134",
            latitude=47.5857,
            longitude=-122.3334,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Seattle Waterfront, Amazon HQ, Pike Place Market, Lumen Field, Space Needle",
            ideal_for="Commercial Development, Invest for Appreciation",
            risk_notes="Environmental due diligence is recommended due to surrounding industrial and logistics uses.",
        ),
        Plot(
            title="West Bellevue Estate Lot Near Meydenbauer Bay",
            description=(
                "Premium Bellevue residential land in a coveted west-side neighborhood "
                "with mature tree cover and luxury-home surroundings. A compelling "
                "blank canvas for a custom residence close to downtown amenities and "
                "lakefront recreation."
            ),
            price=2350000,
            area_acres=0.42,
            city="Bellevue",
            state="WA",
            zip_code="98004",
            latitude=47.6139,
            longitude=-122.2091,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Bellevue Square, Downtown Bellevue, Meydenbauer Center, Meydenbauer Bay Park",
            ideal_for="Build a Home, Retirement / Lifestyle",
            risk_notes="Luxury construction costs, tree retention rules, and design review standards should be evaluated early.",
        ),
        Plot(
            title="Bel-Red Redevelopment Parcel Near Tech Offices",
            description=(
                "Strategic Bellevue parcel in the Bel-Red corridor with strong "
                "redevelopment fundamentals and proximity to major Eastside employers. "
                "Well suited for a commercial or mixed-use concept subject to city "
                "review."
            ),
            price=3250000,
            area_acres=0.61,
            city="Bellevue",
            state="WA",
            zip_code="98005",
            latitude=47.6248,
            longitude=-122.1685,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Microsoft offices, Downtown Bellevue, Bellevue Square, Meydenbauer Center",
            ideal_for="Commercial Development, Maximize Value",
            risk_notes="Entitlement timeline, traffic mitigation, and frontage improvements may materially affect project economics.",
        ),
        Plot(
            title="Somerset Hillside View Lot",
            description=(
                "Elevated Bellevue residential parcel with potential territorial and "
                "skyline views from a thoughtfully designed home. The setting offers "
                "privacy while remaining close to schools, shopping, and Eastside "
                "employment hubs."
            ),
            price=1185000,
            area_acres=0.31,
            city="Bellevue",
            state="WA",
            zip_code="98006",
            latitude=47.5635,
            longitude=-122.1498,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Bellevue Square, Downtown Bellevue, Meydenbauer Center, Microsoft offices",
            ideal_for="Retirement / Lifestyle, Invest for Appreciation",
            risk_notes="Slope, drainage, retaining wall design, and geotechnical review should be completed before permitting.",
        ),
        Plot(
            title="Education Hill Build Lot Near Redmond Town Center",
            description=(
                "Well-located Redmond residential lot in a desirable neighborhood with "
                "quick access to parks, schools, and downtown Redmond amenities. Strong "
                "fit for a custom home or builder-led resale project."
            ),
            price=725000,
            area_acres=0.24,
            city="Redmond",
            state="WA",
            zip_code="98052",
            latitude=47.6832,
            longitude=-122.1169,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Microsoft Campus, Nintendo of America, Marymoor Park, Redmond Town Center",
            ideal_for="Build a Home, Maximize Value",
            risk_notes="Buyer should confirm lot coverage, stormwater requirements, and driveway placement with the city.",
        ),
        Plot(
            title="Marymoor Edge Development Site",
            description=(
                "Redmond parcel near major recreation, employment, and regional trail "
                "connections. The site offers excellent positioning for a compact "
                "residential or live-work concept serving the Eastside tech workforce."
            ),
            price=1450000,
            area_acres=0.48,
            city="Redmond",
            state="WA",
            zip_code="98052",
            latitude=47.6661,
            longitude=-122.1094,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Marymoor Park, Microsoft Campus, Redmond Town Center, Nintendo of America",
            ideal_for="Invest for Appreciation, Commercial Development",
            risk_notes="Adjacent traffic patterns, bike corridor setbacks, and stormwater capacity should be reviewed during feasibility.",
        ),
        Plot(
            title="Overlake Tech Corridor Commercial Lot",
            description=(
                "High-visibility Redmond commercial land in the Overlake area, "
                "surrounded by office, retail, and multifamily demand drivers. A "
                "strong candidate for specialty retail, medical office, or service "
                "commercial development."
            ),
            price=2150000,
            area_acres=0.52,
            city="Redmond",
            state="WA",
            zip_code="98052",
            latitude=47.6419,
            longitude=-122.1317,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Microsoft Campus, Nintendo of America, Redmond Town Center, Marymoor Park",
            ideal_for="Commercial Development, Invest for Appreciation",
            risk_notes="Commercial permitting, parking ratios, and access management requirements may affect final site yield.",
        ),
    ]

    image_data = [
        {
            "image_url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Seattle urban infill lot suitable for a custom home",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Walkable Seattle neighborhood lot with residential build potential",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Seattle commercial development parcel near downtown infrastructure",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Luxury Bellevue residential homesite with mature neighborhood setting",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Bellevue commercial redevelopment parcel near office and retail uses",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Elevated Bellevue hillside homesite with territorial view potential",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Suburban Redmond residential build lot near a quiet neighborhood",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1448630360428-65456885c650?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Green Redmond development parcel near parks and regional trails",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Commercial land near a technology office corridor",
            "is_primary": True,
        },
    ]

    add_plots_with_images(db, plots, image_data)
    print(f"Seeded {len(plots)} Washington plots.")


def seed_texas(db) -> None:
    plots = [
        Plot(
            title="Lake Travis View Homesite Near Steiner Ranch",
            description=(
                "Elevated residential parcel west of Austin with long Hill Country "
                "sightlines and strong custom-home demand. The site works well for "
                "a primary residence or luxury weekend base with convenient access "
                "to marinas, schools, and the Austin tech corridor."
            ),
            price=485000,
            area_acres=1.18,
            city="Austin",
            state="TX",
            zip_code="78732",
            latitude=30.3838,
            longitude=-97.8936,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=False,
            nearby_landmarks="Lake Travis, Steiner Ranch, The Domain, Downtown Austin",
            ideal_for="Build a Home, Retirement / Lifestyle, Invest for Appreciation",
            risk_notes="Septic design, slope, and wildfire interface considerations should be reviewed during feasibility.",
        ),
        Plot(
            title="East Austin Infill Lot Near Mueller",
            description=(
                "Compact urban lot in a fast-changing East Austin pocket with nearby "
                "retail, parks, and employment access. Strong candidate for a modern "
                "infill home, detached guest unit strategy, or long-term appreciation play."
            ),
            price=395000,
            area_acres=0.14,
            city="Austin",
            state="TX",
            zip_code="78723",
            latitude=30.2989,
            longitude=-97.6905,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Mueller Lake Park, Downtown Austin, The Domain, University of Texas at Austin",
            ideal_for="Build a Home, Maximize Value, Invest for Appreciation",
            risk_notes="Buyer should verify impervious cover limits, tree protections, and alley utility locations.",
        ),
        Plot(
            title="Dallas Medical District Commercial Corner",
            description=(
                "High-visibility commercial parcel near major healthcare and airport "
                "demand drivers. The lot is positioned for medical office, specialty "
                "retail, or a service business seeking strong daily traffic and central Dallas access."
            ),
            price=820000,
            area_acres=0.62,
            city="Dallas",
            state="TX",
            zip_code="75235",
            latitude=32.8129,
            longitude=-96.8387,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="UT Southwestern Medical Center, Dallas Love Field, Downtown Dallas, Design District",
            ideal_for="Commercial Development, Invest for Appreciation",
            risk_notes="Traffic access, parking ratios, and commercial signage restrictions should be confirmed.",
        ),
        Plot(
            title="Houston East End Logistics Redevelopment Site",
            description=(
                "Urban commercial land with strong industrial and last-mile delivery "
                "fundamentals near port and freeway routes. Suitable for contractor "
                "storage, flex warehouse, or a small logistics-oriented redevelopment project."
            ),
            price=540000,
            area_acres=1.35,
            city="Houston",
            state="TX",
            zip_code="77029",
            latitude=29.7524,
            longitude=-95.2662,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Port of Houston, Buffalo Bayou, Downtown Houston, I-610",
            ideal_for="Commercial Development, Maximize Value, Invest for Appreciation",
            risk_notes="Floodplain status, drainage capacity, and environmental history should be evaluated before closing.",
        ),
        Plot(
            title="San Antonio Northside Family Build Acre",
            description=(
                "Usable residential acreage in a growing northwest San Antonio corridor "
                "with space for a custom home, workshop, and outdoor living. The property "
                "offers better value than tighter subdivision lots while staying close to shopping."
            ),
            price=175000,
            area_acres=1.12,
            city="San Antonio",
            state="TX",
            zip_code="78253",
            latitude=29.4712,
            longitude=-98.7581,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=False,
            nearby_landmarks="River Walk, Alamo Ranch, SeaWorld San Antonio, Loop 1604",
            ideal_for="Build a Home, Maximize Value",
            risk_notes="Septic feasibility and utility tap costs should be confirmed with local providers.",
        ),
        Plot(
            title="Plano Legacy Business District Pad Site",
            description=(
                "Small commercial pad site near one of North Texas' strongest office "
                "and retail markets. The parcel fits professional services, quick-service "
                "retail, or a boutique owner-user concept near major corporate campuses."
            ),
            price=1250000,
            area_acres=0.74,
            city="Plano",
            state="TX",
            zip_code="75024",
            latitude=33.0812,
            longitude=-96.8218,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Toyota HQ, Legacy West, The Shops at Legacy, Dallas North Tollway",
            ideal_for="Commercial Development, Invest for Appreciation",
            risk_notes="Premium land basis requires careful review of site yield, parking, and access easements.",
        ),
        Plot(
            title="Frisco Residential Lot Near The Star",
            description=(
                "Infill residential parcel in a high-growth Frisco location with strong "
                "school, sports, and corporate demand drivers. A builder or end user "
                "could position a new home for excellent resale depth in the North Dallas market."
            ),
            price=430000,
            area_acres=0.28,
            city="Frisco",
            state="TX",
            zip_code="75034",
            latitude=33.1041,
            longitude=-96.8264,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="The Star, Legacy West, Toyota HQ, Frisco Square",
            ideal_for="Build a Home, Invest for Appreciation, Maximize Value",
            risk_notes="Buyer should verify HOA architectural standards and city impact fees before design work.",
        ),
        Plot(
            title="Fredericksburg Wine Country Ranch Tract",
            description=(
                "Scenic Hill Country tract with open pasture, native trees, and strong "
                "lifestyle appeal near wineries and downtown Fredericksburg. Well suited "
                "for a weekend retreat, short-term rental concept, or long-term land hold."
            ),
            price=695000,
            area_acres=8.75,
            city="Fredericksburg",
            state="TX",
            zip_code="78624",
            latitude=30.2754,
            longitude=-98.8717,
            zoning_type="ranch",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=False,
            electricity=True,
            sewer=False,
            nearby_landmarks="Main Street Fredericksburg, Enchanted Rock, Texas Wine Trail, Lady Bird Johnson Municipal Park",
            ideal_for="Retirement / Lifestyle, Invest for Appreciation, Maximize Value",
            risk_notes="Well drilling, septic design, and short-term rental rules should be verified before development.",
        ),
    ]

    image_data = [
        {
            "image_url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Hill Country homesite with open views near Lake Travis",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Urban residential infill lot suitable for a modern Austin home",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Dallas commercial corner lot near a medical and business district",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Houston industrial logistics land near port infrastructure",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "San Antonio suburban residential acreage for a family home",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1531973576160-7125cd663d86?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Plano commercial pad site near corporate offices and retail",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Residential lot in a high-growth Frisco suburb",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Open ranch land in Texas Hill Country",
            "is_primary": True,
        },
    ]

    add_plots_with_images(db, plots, image_data)
    print(f"Seeded {len(plots)} Texas plots.")


def seed_arizona(db) -> None:
    plots = [
        Plot(
            title="Phoenix Arcadia Lite Infill Homesite",
            description=(
                "Prime infill lot in a central Phoenix neighborhood with strong luxury "
                "renovation and new-build demand. The site is a fit for a modern desert "
                "residence near restaurants, employment centers, and outdoor recreation."
            ),
            price=525000,
            area_acres=0.21,
            city="Phoenix",
            state="AZ",
            zip_code="85018",
            latitude=33.4965,
            longitude=-111.9884,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Camelback Mountain, Desert Botanical Garden, Biltmore Fashion Park, Papago Park",
            ideal_for="Build a Home, Invest for Appreciation",
            risk_notes="Buyer should confirm setbacks, demolition requirements, and irrigation district details if applicable.",
        ),
        Plot(
            title="North Scottsdale Desert Estate Lot",
            description=(
                "Luxury desert homesite with privacy, mountain character, and access "
                "to upscale shopping, golf, and resort amenities. The parcel is suited "
                "for a custom estate designed around outdoor living and Sonoran Desert views."
            ),
            price=1180000,
            area_acres=2.35,
            city="Scottsdale",
            state="AZ",
            zip_code="85255",
            latitude=33.6822,
            longitude=-111.8756,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=False,
            nearby_landmarks="Scottsdale Fashion Square, McDowell Sonoran Preserve, Camelback Mountain, Troon North",
            ideal_for="Build a Home, Retirement / Lifestyle, Invest for Appreciation",
            risk_notes="Septic planning, native plant preservation, and hillside design standards may affect build cost.",
        ),
        Plot(
            title="Mesa Gateway Growth Corridor Parcel",
            description=(
                "Residential development parcel in southeast Mesa near expanding "
                "employment, airport, and education anchors. The site offers a value "
                "oriented entry into a growth corridor with family-home demand."
            ),
            price=410000,
            area_acres=1.05,
            city="Mesa",
            state="AZ",
            zip_code="85212",
            latitude=33.3345,
            longitude=-111.6518,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Arizona State University Polytechnic campus, Phoenix-Mesa Gateway Airport, Usery Mountain Regional Park",
            ideal_for="Build a Home, Maximize Value, Invest for Appreciation",
            risk_notes="Buyer should verify utility extension costs and subdivision feasibility with the city.",
        ),
        Plot(
            title="Chandler Tech Corridor Commercial Lot",
            description=(
                "Well-positioned commercial parcel near Chandler's semiconductor and "
                "office employment base. The property fits specialty retail, daycare, "
                "medical office, or service commercial use supporting nearby residential growth."
            ),
            price=950000,
            area_acres=0.83,
            city="Chandler",
            state="AZ",
            zip_code="85286",
            latitude=33.2726,
            longitude=-111.8753,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Downtown Chandler, Intel Ocotillo Campus, Chandler Fashion Center, Arizona State University",
            ideal_for="Commercial Development, Invest for Appreciation",
            risk_notes="Access design, parking count, and heat-island landscaping requirements should be reviewed.",
        ),
        Plot(
            title="Sedona Red Rock Retreat Parcel",
            description=(
                "Scenic lifestyle parcel with dramatic red rock surroundings and strong "
                "appeal for a retreat home or high-end second-home buyer. The location "
                "balances quiet desert living with access to galleries, trails, and visitor demand."
            ),
            price=645000,
            area_acres=0.78,
            city="Sedona",
            state="AZ",
            zip_code="86336",
            latitude=34.8697,
            longitude=-111.7609,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=False,
            nearby_landmarks="Sedona Red Rocks, Tlaquepaque Arts and Shopping Village, Cathedral Rock, Airport Mesa",
            ideal_for="Retirement / Lifestyle, Build a Home, Invest for Appreciation",
            risk_notes="Short-term rental rules, septic feasibility, and view corridor restrictions should be confirmed.",
        ),
        Plot(
            title="Flagstaff Mountain Cabin Homesite",
            description=(
                "Ponderosa pine lot near Flagstaff recreation and university demand "
                "drivers. The parcel is well suited for a mountain cabin, year-round "
                "residence, or long-term lifestyle hold with cooler summer temperatures."
            ),
            price=285000,
            area_acres=0.96,
            city="Flagstaff",
            state="AZ",
            zip_code="86004",
            latitude=35.2134,
            longitude=-111.5778,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=False,
            electricity=True,
            sewer=False,
            nearby_landmarks="Lowell Observatory, Northern Arizona University, Arizona Snowbowl, Walnut Canyon National Monument",
            ideal_for="Retirement / Lifestyle, Build a Home, Maximize Value",
            risk_notes="Well, septic, snow access, and wildfire mitigation should be evaluated before construction.",
        ),
        Plot(
            title="Scottsdale Retirement Patio Home Lot",
            description=(
                "Low-maintenance residential lot near healthcare, golf, and shopping "
                "amenities. A practical fit for a lock-and-leave retirement home or "
                "seasonal desert residence with strong resale appeal."
            ),
            price=390000,
            area_acres=0.16,
            city="Scottsdale",
            state="AZ",
            zip_code="85258",
            latitude=33.5692,
            longitude=-111.8998,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Scottsdale Fashion Square, Talking Stick Resort, Camelback Mountain, McCormick Ranch",
            ideal_for="Retirement / Lifestyle, Build a Home",
            risk_notes="HOA design standards and drainage requirements should be verified before plan submission.",
        ),
    ]

    image_data = [
        {
            "image_url": "https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Central Phoenix residential infill lot with desert landscaping",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1523217582562-09d0def993a6?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Luxury Sonoran Desert homesite in North Scottsdale",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Growth corridor residential land in Mesa Arizona",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1494522855154-9297ac14b55f?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Commercial land near a modern Arizona office corridor",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Scenic red rock lifestyle land in Sedona",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Wooded mountain cabin homesite near Flagstaff",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Low-maintenance Scottsdale residential lot for retirement living",
            "is_primary": True,
        },
    ]

    add_plots_with_images(db, plots, image_data)
    print(f"Seeded {len(plots)} Arizona plots.")


def seed_florida(db) -> None:
    plots = [
        Plot(
            title="Orlando Vacation Rental Infill Lot Near Attractions",
            description=(
                "Residential lot positioned for vacation-home demand west of Orlando's "
                "core tourism corridor. The parcel is suited for a family home, seasonal "
                "rental, or furnished short-stay strategy subject to local rules."
            ),
            price=315000,
            area_acres=0.22,
            city="Orlando",
            state="FL",
            zip_code="32819",
            latitude=28.4569,
            longitude=-81.4702,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Universal Orlando, Walt Disney World, International Drive, Orange County Convention Center",
            ideal_for="Build a Home, Invest for Appreciation, Maximize Value",
            risk_notes="Short-term rental eligibility, HOA rules, and stormwater requirements should be confirmed.",
        ),
        Plot(
            title="Tampa River District Commercial Parcel",
            description=(
                "Urban commercial land near downtown Tampa's riverfront growth corridor. "
                "The site offers strong visibility for retail, small hospitality, or "
                "service use serving residents, office workers, and visitors."
            ),
            price=925000,
            area_acres=0.31,
            city="Tampa",
            state="FL",
            zip_code="33602",
            latitude=27.9528,
            longitude=-82.4626,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Tampa Riverwalk, Amalie Arena, Water Street Tampa, Armature Works",
            ideal_for="Commercial Development, Invest for Appreciation",
            risk_notes="Flood zone status, parking requirements, and urban design standards should be reviewed.",
        ),
        Plot(
            title="Miami Little River Redevelopment Lot",
            description=(
                "Miami infill parcel in a redevelopment corridor with access to design, "
                "arts, and employment districts. The property is positioned for townhomes, "
                "small multifamily, or a mixed-use concept subject to zoning confirmation."
            ),
            price=1350000,
            area_acres=0.24,
            city="Miami",
            state="FL",
            zip_code="33138",
            latitude=25.8342,
            longitude=-80.1888,
            zoning_type="mixed-use",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="South Beach, Wynwood Walls, Miami Design District, Biscayne Bay",
            ideal_for="Commercial Development, Invest for Appreciation, Maximize Value",
            risk_notes="Flood elevation, sea-level resilience, and entitlement timing may materially affect project cost.",
        ),
        Plot(
            title="Sarasota Bay Lifestyle Homesite",
            description=(
                "Residential parcel near Sarasota's bayfront, arts venues, and beach "
                "access. The location is a strong match for a retirement residence, "
                "vacation home, or premium coastal lifestyle build."
            ),
            price=585000,
            area_acres=0.27,
            city="Sarasota",
            state="FL",
            zip_code="34236",
            latitude=27.3311,
            longitude=-82.5457,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Sarasota Bay, St. Armands Circle, Marie Selby Botanical Gardens, Lido Key Beach",
            ideal_for="Retirement / Lifestyle, Build a Home, Invest for Appreciation",
            risk_notes="Coastal flood insurance, wind-load construction standards, and tree rules should be reviewed.",
        ),
        Plot(
            title="Naples Gulf Access Residential Lot",
            description=(
                "Premium Naples homesite near beach, boating, and upscale retail amenities. "
                "The parcel is well suited for a luxury retirement home or seasonal "
                "residence with strong long-term land value fundamentals."
            ),
            price=1450000,
            area_acres=0.29,
            city="Naples",
            state="FL",
            zip_code="34102",
            latitude=26.1506,
            longitude=-81.7959,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Naples Pier, Fifth Avenue South, Gulf of Mexico, Everglades National Park",
            ideal_for="Retirement / Lifestyle, Build a Home, Invest for Appreciation",
            risk_notes="High insurance costs, floodplain elevation, and coastal construction standards should be evaluated.",
        ),
        Plot(
            title="Jacksonville Beach Family Build Lot",
            description=(
                "Coastal-area residential lot offering access to beaches, schools, and "
                "commuter routes. The site is a practical fit for a family home or "
                "long-term appreciation play in a growing northeast Florida market."
            ),
            price=365000,
            area_acres=0.18,
            city="Jacksonville",
            state="FL",
            zip_code="32250",
            latitude=30.2852,
            longitude=-81.4107,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Jacksonville Beach, Mayo Clinic Jacksonville, St. Johns Town Center, Atlantic Beach",
            ideal_for="Build a Home, Invest for Appreciation, Maximize Value",
            risk_notes="Buyer should verify coastal setback rules, drainage, and windstorm insurance assumptions.",
        ),
        Plot(
            title="St. Petersburg Kenwood Infill Lot",
            description=(
                "Urban residential parcel in a character-rich St. Petersburg neighborhood "
                "near downtown, waterfront parks, and arts districts. A strong fit for "
                "a new bungalow, ADU strategy, or boutique rental hold."
            ),
            price=285000,
            area_acres=0.13,
            city="St. Petersburg",
            state="FL",
            zip_code="33713",
            latitude=27.7769,
            longitude=-82.6681,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Tampa Bay, St. Pete Pier, Tropicana Field, Clearwater Beach",
            ideal_for="Build a Home, Maximize Value, Invest for Appreciation",
            risk_notes="Lot coverage, alley access, and local ADU rules should be confirmed before design.",
        ),
        Plot(
            title="Orlando Lake Nona Medical City Pad",
            description=(
                "Commercial parcel in a high-growth southeast Orlando corridor near "
                "healthcare, education, and residential expansion. The site is suited "
                "for medical office, wellness retail, or neighborhood service commercial use."
            ),
            price=1100000,
            area_acres=0.86,
            city="Orlando",
            state="FL",
            zip_code="32827",
            latitude=28.3712,
            longitude=-81.2789,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Lake Nona Medical City, Orlando International Airport, Walt Disney World, Universal Orlando",
            ideal_for="Commercial Development, Invest for Appreciation",
            risk_notes="Traffic concurrency, stormwater retention, and final site plan approval should be reviewed.",
        ),
    ]

    image_data = [
        {
            "image_url": "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Orlando residential vacation home lot near attractions",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1444723121867-7a241cacace9?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Tampa urban commercial parcel near downtown riverfront",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Miami urban redevelopment land near mixed-use districts",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Sarasota coastal lifestyle homesite near the bay",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Naples luxury coastal residential lot near the Gulf",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Jacksonville Beach area residential build lot",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1572120360610-d971b9d7767c?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "St. Petersburg infill lot near downtown neighborhoods",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Orlando commercial pad site near medical and airport growth",
            "is_primary": True,
        },
    ]

    add_plots_with_images(db, plots, image_data)
    print(f"Seeded {len(plots)} Florida plots.")


def seed_new_york(db) -> None:
    plots = [
        Plot(
            title="Manhattan West Side Redevelopment Parcel",
            description=(
                "Rare urban redevelopment land on Manhattan's west side with exceptional "
                "access to transit, office demand, and luxury residential drivers. The "
                "site is best suited for a sophisticated mixed-use or boutique residential project."
            ),
            price=9800000,
            area_acres=0.09,
            city="New York City",
            state="NY",
            zip_code="10018",
            latitude=40.7548,
            longitude=-73.9972,
            zoning_type="mixed-use",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Hudson Yards, Times Square, Central Park, Penn Station",
            ideal_for="Commercial Development, Invest for Appreciation, Maximize Value",
            risk_notes="Entitlements, air rights, environmental review, and construction logistics require specialized due diligence.",
        ),
        Plot(
            title="Brooklyn Gowanus Mixed-Use Development Site",
            description=(
                "Brooklyn redevelopment parcel in a high-demand mixed-use corridor near "
                "transit, retail, and brownstone neighborhoods. The property is positioned "
                "for boutique residential over ground-floor commercial."
            ),
            price=4200000,
            area_acres=0.16,
            city="Brooklyn",
            state="NY",
            zip_code="11215",
            latitude=40.6764,
            longitude=-73.9902,
            zoning_type="mixed-use",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Brooklyn Bridge, Prospect Park, Barclays Center, Gowanus Canal",
            ideal_for="Commercial Development, Invest for Appreciation",
            risk_notes="Environmental remediation, floodplain rules, and rezoning compliance should be verified before acquisition.",
        ),
        Plot(
            title="Queens Transit-Oriented Infill Lot Near Flushing",
            description=(
                "Dense Queens infill parcel with strong access to transit, airport demand, "
                "and neighborhood retail. The site fits a small residential or mixed-use "
                "project serving a deep local rental and ownership market."
            ),
            price=2250000,
            area_acres=0.12,
            city="Queens",
            state="NY",
            zip_code="11355",
            latitude=40.7577,
            longitude=-73.8292,
            zoning_type="mixed-use",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="LaGuardia Airport, JFK Airport, Flushing Meadows Corona Park, Citi Field",
            ideal_for="Commercial Development, Invest for Appreciation, Maximize Value",
            risk_notes="Buyer should review FAR, parking waivers, curb-cut availability, and construction staging constraints.",
        ),
        Plot(
            title="Long Island Sound Residential Homesite",
            description=(
                "North Shore residential parcel with mature surroundings and access to "
                "waterfront villages, commuter routes, and recreation. A strong candidate "
                "for a custom home or lifestyle hold within reach of New York City."
            ),
            price=875000,
            area_acres=0.64,
            city="Long Island",
            state="NY",
            zip_code="11050",
            latitude=40.8407,
            longitude=-73.7118,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Long Island Sound, Port Washington, Manhasset Bay, LaGuardia Airport",
            ideal_for="Build a Home, Retirement / Lifestyle, Invest for Appreciation",
            risk_notes="Local village approvals, tree removal rules, and coastal drainage should be confirmed.",
        ),
        Plot(
            title="White Plains Metro-North Apartment Site",
            description=(
                "Transit-oriented development parcel near downtown White Plains with "
                "strong commuter, healthcare, and office demand. The site is suited for "
                "multifamily or mixed-use redevelopment with excellent regional connectivity."
            ),
            price=3150000,
            area_acres=0.38,
            city="White Plains",
            state="NY",
            zip_code="10601",
            latitude=41.0339,
            longitude=-73.7648,
            zoning_type="mixed-use",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Metro-North, The Westchester, White Plains Hospital, Downtown White Plains",
            ideal_for="Commercial Development, Invest for Appreciation, Maximize Value",
            risk_notes="Site plan approval, affordable housing requirements, and parking strategy should be evaluated.",
        ),
        Plot(
            title="Yonkers Hudson View Residential Lot",
            description=(
                "Hillside residential parcel in Yonkers with potential Hudson River "
                "outlooks and access to commuter rail. The property fits a custom home "
                "or small builder project in a market benefiting from Westchester spillover demand."
            ),
            price=495000,
            area_acres=0.21,
            city="Yonkers",
            state="NY",
            zip_code="10701",
            latitude=40.9401,
            longitude=-73.8958,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Metro-North, Hudson River Museum, Untermyer Park, Van Cortlandt Park",
            ideal_for="Build a Home, Maximize Value, Invest for Appreciation",
            risk_notes="Slope, retaining wall design, and utility tie-ins should be reviewed before permitting.",
        ),
        Plot(
            title="Albany Warehouse District Commercial Lot",
            description=(
                "Commercial redevelopment parcel in Albany's warehouse district near "
                "breweries, apartments, and state government employment. The site is "
                "positioned for flex commercial, small mixed-use, or an owner-user building."
            ),
            price=385000,
            area_acres=0.52,
            city="Albany",
            state="NY",
            zip_code="12207",
            latitude=42.6609,
            longitude=-73.7508,
            zoning_type="commercial",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Empire State Plaza, Albany Capital Center, Hudson River, New York State Capitol",
            ideal_for="Commercial Development, Maximize Value, Invest for Appreciation",
            risk_notes="Environmental history, winter construction costs, and adaptive-use zoning standards should be reviewed.",
        ),
        Plot(
            title="Brooklyn Prospect-Lefferts Residential Infill Lot",
            description=(
                "Small Brooklyn residential parcel near park access, transit, and "
                "established rowhouse blocks. The site is a strong candidate for a "
                "boutique townhouse, two-family residence, or long-term land hold."
            ),
            price=1650000,
            area_acres=0.07,
            city="Brooklyn",
            state="NY",
            zip_code="11225",
            latitude=40.6602,
            longitude=-73.9571,
            zoning_type="residential",
            listing_type="sale",
            status="available",
            road_access=True,
            water_access=True,
            electricity=True,
            sewer=True,
            nearby_landmarks="Prospect Park, Brooklyn Botanic Garden, Brooklyn Museum, Brooklyn Bridge",
            ideal_for="Build a Home, Invest for Appreciation, Maximize Value",
            risk_notes="Narrow-lot design, party-wall conditions, and DOB approval timeline should be carefully budgeted.",
        ),
    ]

    image_data = [
        {
            "image_url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Manhattan urban redevelopment parcel near high-rise buildings",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1518391846015-55a9cc003b25?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Brooklyn mixed-use redevelopment site near transit and rowhouses",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Queens transit-oriented infill parcel near airport corridors",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Long Island residential homesite near waterfront and mature trees",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "White Plains transit-oriented mixed-use development parcel",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Yonkers hillside residential lot with Hudson Valley character",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Albany commercial redevelopment land near downtown",
            "is_primary": True,
        },
        {
            "image_url": "https://images.unsplash.com/photo-1598228723793-52759bba239c?auto=format&fit=crop&w=1200&q=80",
            "alt_text": "Brooklyn residential infill parcel near park and rowhouse streets",
            "is_primary": True,
        },
    ]

    add_plots_with_images(db, plots, image_data)
    print(f"Seeded {len(plots)} New York plots.")


RESET_DB = True

def main() -> None:
    db = SessionLocal()

    try:
        if RESET_DB:
            print("Resetting demo data...")
            reset_demo_data(db)
        else:
            print("Skipping demo data reset. Using existing data.")
        seed_california(db)
        seed_washington(db)
        seed_texas(db)
        seed_arizona(db)
        seed_florida(db)
        seed_new_york(db)
        print("Done. Seeded demo plots and primary images.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
