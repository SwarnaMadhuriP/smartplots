from datetime import datetime
from typing import Optional, cast

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import re
from sqlalchemy import or_
from .database import Base, engine

# Ensure pgvector extension is enabled in PostgreSQL
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()


class Plot(Base):
    __tablename__ = "plots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    price: Mapped[float] = mapped_column(Float, nullable=False)
    area_acres: Mapped[float] = mapped_column(Float, nullable=False)

    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    zip_code: Mapped[Optional[str]] = mapped_column(String)

    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)

    zoning_type: Mapped[Optional[str]] = mapped_column(String)
    listing_type: Mapped[Optional[str]] = mapped_column(String, default="sale")
    status: Mapped[Optional[str]] = mapped_column(String, default="available")

    road_access: Mapped[bool] = mapped_column(Boolean, default=False)
    water_access: Mapped[bool] = mapped_column(Boolean, default=False)
    electricity: Mapped[bool] = mapped_column(Boolean, default=False)
    sewer: Mapped[bool] = mapped_column(Boolean, default=False)

    nearby_landmarks: Mapped[Optional[str]] = mapped_column(Text)
    ideal_for: Mapped[Optional[str]] = mapped_column(Text)
    risk_notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    images: Mapped[list["PlotImage"]] = relationship(
        "PlotImage", back_populates="plot", cascade="all, delete-orphan"
    )
    insight: Mapped[Optional["PlotInsight"]] = relationship(
        "PlotInsight",
        back_populates="plot",
        uselist=False,
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="plot", cascade="all, delete-orphan"
    )

    @property
    def computed_risk_level(self) -> str:
        if self.insight and self.insight.risk_level:
            return self.insight.risk_level
        # pyrefly: ignore [unsupported-operation]
        risk_text = ((self.risk_notes or "") + " " + (self.description or "")).lower()
        missing_utilities = sum(
            1
            for u in [self.road_access, self.water_access, self.electricity, self.sewer]
            if not u
        )
        if "flood" in risk_text or "hazard" in risk_text or missing_utilities >= 3:
            return "High"
        elif (
            "limited" in risk_text
            or "restriction" in risk_text
            or missing_utilities >= 1
            or "noise" in risk_text
            or "competition" in risk_text
        ):
            return "Medium"
        return "Low"

    @property
    def computed_rental_demand(self) -> str:
        if self.zoning_type == "commercial":
            return "High"
        elif self.zoning_type == "residential":
            return "High" if (self.road_access and self.water_access) else "Medium"
        else:  # agricultural/other
            return "Medium" if self.water_access else "Low"

    @property
    def computed_liquidity(self) -> str:
        missing_utilities = sum(
            1
            for u in [self.road_access, self.water_access, self.electricity, self.sewer]
            if not u
        )
        if missing_utilities == 0 and self.zoning_type in ["commercial", "residential"]:
            return "High"
        elif missing_utilities >= 2 or self.zoning_type == "agricultural":
            return "Low"
        else:
            return "Moderate"

    @property
    def computed_appreciation(self) -> str:
        if self.insight and self.insight.growth_potential:
            return self.insight.growth_potential
        desc_text = (
            # pyrefly: ignore [unsupported-operation]
            (self.description or "") + " " + (self.nearby_landmarks or "")
        ).lower()
        if (
            "downtown" in desc_text
            or "rapidly growing" in desc_text
            or "suburb" in desc_text
            or "highway" in desc_text
        ):
            return "High"
        missing_utilities = sum(
            1
            for u in [self.road_access, self.water_access, self.electricity, self.sewer]
            if not u
        )
        if "rural" in desc_text or "farming" in desc_text or missing_utilities >= 2:
            return "Low"
        return "Moderate"

    @property
    def computed_match_score(self) -> int:
        if self.insight and self.insight.investment_score is not None:
            db_score = self.insight.investment_score
            return round(db_score / 10) if db_score > 10 else db_score

        score = 4  # Base score
        if self.road_access:
            score += 1
        if self.water_access:
            score += 1
        if self.electricity:
            score += 1
        if self.sewer:
            score += 1

        if self.zoning_type in ["commercial", "residential"]:
            score += 2
        else:
            score += 1

        if self.computed_appreciation == "High":
            score += 2
        elif self.computed_appreciation == "Moderate":
            score += 1

        if self.computed_risk_level == "Low":
            score += 2
        elif self.computed_risk_level == "Medium":
            score += 1

        return max(1, min(10, score - 2))

    def to_json_dict(self) -> dict:
        primary_image = None
        if self.images:
            primary = next(
                (img for img in self.images if img.is_primary),
                self.images[0],
            )
            primary_image = primary.image_url

        reasons = []
        if self.road_access:
            reasons.append("Road access is available")
        if self.water_access:
            reasons.append("Water access is available")
        if self.electricity:
            reasons.append("Electricity connection is available")
        if self.sewer:
            reasons.append("Sewer connection is available")
        if self.nearby_landmarks:
            reasons.append(f"Nearby landmarks: {self.nearby_landmarks}")
        if self.zoning_type:
            reasons.append(f"Zoned for {self.zoning_type.lower()} use")
        if self.ideal_for:
            reasons.append(f"Suitable for {self.ideal_for}")
        if not reasons:
            reasons.append("Matches basic land search criteria")

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image": primary_image or "/placeholder-plot.jpg",
            "location": f"{self.city}, {self.state}",
            "latitude": self.latitude,
            "longitude": self.longitude,
            "price": f"${self.price:,.0f}",
            "acres": f"{self.area_acres} Acres",
            "zone": self.zoning_type or "General",
            "matchScore": self.computed_match_score,
            "appreciation": self.computed_appreciation,
            "rentalDemand": self.computed_rental_demand,
            "liquidity": self.computed_liquidity,
            "riskLevel": self.computed_risk_level,
            "reasons": reasons[:3],
            "highlights": [item.strip() for item in self.ideal_for.split(",")]
            if self.ideal_for
            else ["Suitable for residential or investment use"],
        }


def apply_plot_search_filters(query, search: str):
    search_lower = search.lower().strip()

    # 1. Parse Acres / Area expressions
    # Example: "between 1.5 and 3 acres", "between 1 and 2 ac"
    between_area_match = re.search(
        r"between\s+(\d+(?:\.\d+)?)\s*(?:acres|acre|ac)?\s+and\s+(\d+(?:\.\d+)?)\s*(?:acres|acre|ac)",
        search_lower,
    )
    if between_area_match:
        min_area = float(between_area_match.group(1))
        max_area = float(between_area_match.group(2))
        query = query.filter(Plot.area_acres >= min_area, Plot.area_acres <= max_area)
        search_lower = search_lower.replace(between_area_match.group(0), "")

    # Example: "under 2 acres", "below 1.5 acre", "less than 1 ac"
    max_area_match = re.search(
        r"(under|below|less than)\s+(\d+(?:\.\d+)?)\s*(?:acres|acre|ac)",
        search_lower,
    )
    if max_area_match:
        max_area = float(max_area_match.group(2))
        query = query.filter(Plot.area_acres <= max_area)
        search_lower = search_lower.replace(max_area_match.group(0), "")

    # Example: "above 1 acre", "over 2 acres", "greater than 0.5 acre", "more than 3 ac"
    min_area_match = re.search(
        r"(above|over|greater than|more than)\s+(\d+(?:\.\d+)?)\s*(?:acres|acre|ac)",
        search_lower,
    )
    if min_area_match:
        min_area = float(min_area_match.group(2))
        query = query.filter(Plot.area_acres >= min_area)
        search_lower = search_lower.replace(min_area_match.group(0), "")

    # Example: standalone area like "1.5 acres", "2 acre"
    standalone_area_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(?:acres|acre|ac)\b",
        search_lower,
    )
    if standalone_area_match:
        target_area = float(standalone_area_match.group(1))
        query = query.filter(Plot.area_acres >= target_area)
        search_lower = search_lower.replace(standalone_area_match.group(0), "")

    # 2. Parse Utilities / Access (with support for "no", "without")
    # Water
    if "no water" in search_lower or "without water" in search_lower:
        query = query.filter(Plot.water_access.is_(False))
        search_lower = re.sub(
            r"\b(?:no|without)\s+water\s*(?:access)?\b", "", search_lower
        )
    elif "water" in search_lower:
        query = query.filter(Plot.water_access.is_(True))
        search_lower = re.sub(r"\bwater\s*(?:access)?\b", "", search_lower)

    # Road
    if "no road" in search_lower or "without road" in search_lower:
        query = query.filter(Plot.road_access.is_(False))
        search_lower = re.sub(
            r"\b(?:no|without)\s+road\s*(?:access)?\b", "", search_lower
        )
    elif "road" in search_lower:
        query = query.filter(Plot.road_access.is_(True))
        search_lower = re.sub(r"\broad\s*(?:access)?\b", "", search_lower)

    # Electricity
    if (
        "no electricity" in search_lower
        or "without electricity" in search_lower
        or "no power" in search_lower
        or "without power" in search_lower
    ):
        query = query.filter(Plot.electricity.is_(False))
        search_lower = re.sub(
            r"\b(?:no|without)\s+(?:electricity|electric|power)\b", "", search_lower
        )
    elif (
        "electricity" in search_lower
        or "electric" in search_lower
        or "power" in search_lower
    ):
        query = query.filter(Plot.electricity.is_(True))
        search_lower = re.sub(r"\b(?:electricity|electric|power)\b", "", search_lower)

    # Sewer
    if "no sewer" in search_lower or "without sewer" in search_lower:
        query = query.filter(Plot.sewer.is_(False))
        search_lower = re.sub(r"\b(?:no|without)\s+sewer\b", "", search_lower)
    elif "sewer" in search_lower or "sewage" in search_lower:
        query = query.filter(Plot.sewer.is_(True))
        search_lower = re.sub(r"\b(?:sewer|sewage)\b", "", search_lower)

    # 3. Parse Price expressions
    between_match = re.search(
        r"between\s+(\d+)\s*(k)?\s+and\s+(\d+)\s*(k)?",
        search_lower,
    )
    if between_match:
        min_price = int(between_match.group(1))
        max_price = int(between_match.group(3))
        if between_match.group(2) == "k":
            min_price *= 1000
        if between_match.group(4) == "k":
            max_price *= 1000
        query = query.filter(Plot.price >= min_price, Plot.price <= max_price)
        search_lower = search_lower.replace(between_match.group(0), "")

    # Example: "under 50k", "below 50k", "less than 50k"
    max_match = re.search(
        r"(under|below|less than)\s+(\d+)\s*(k)?",
        search_lower,
    )
    if max_match:
        max_price = int(max_match.group(2))
        if max_match.group(3) == "k":
            max_price *= 1000
        query = query.filter(Plot.price <= max_price)
        search_lower = search_lower.replace(max_match.group(0), "")

    # Example: "above 30k", "over 30k", "greater than 30k", "more than 30k"
    min_match = re.search(
        r"(above|over|greater than|more than)\s+(\d+)\s*(k)?",
        search_lower,
    )
    if min_match:
        min_price = int(min_match.group(2))
        if min_match.group(3) == "k":
            min_price *= 1000
        query = query.filter(Plot.price >= min_price)
        search_lower = search_lower.replace(min_match.group(0), "")

    # Example: standalone price like "100k" or "85000" (budget limit)
    standalone_price_match = re.search(
        r"\b(\d+)\s*(k)\b|\b(\d{4,})\b",
        search_lower,
    )
    if standalone_price_match:
        if standalone_price_match.group(1):
            max_price = int(standalone_price_match.group(1)) * 1000
        else:
            max_price = int(standalone_price_match.group(3))
        query = query.filter(Plot.price <= max_price)
        search_lower = search_lower.replace(standalone_price_match.group(0), "")

    # 4. Keyword search on remaining words
    filler_words = {
        "land",
        "plot",
        "plots",
        "for",
        "in",
        "near",
        "at",
        "show",
        "me",
        "find",
        "looking",
        "want",
        "with",
        "than",
        "like",
        "and",
        "or",
        "a",
        "an",
        "the",
        "to",
        "has",
        "have",
        "without",
    }

    keywords = [
        word
        for word in search_lower.split()
        if word not in filler_words and not word.replace("k", "").isdigit()
    ]

    for word in keywords:
        query = query.filter(
            or_(
                Plot.city.ilike(f"%{word}%"),
                Plot.state.ilike(f"%{word}%"),
                Plot.title.ilike(f"%{word}%"),
                Plot.zoning_type.ilike(f"%{word}%"),
                Plot.ideal_for.ilike(f"%{word}%"),
            )
        )

    return query


class PlotImage(Base):
    __tablename__ = "plot_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("plots.id"), nullable=False
    )

    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    plot: Mapped["Plot"] = relationship("Plot", back_populates="images")


class PlotInsight(Base):
    __tablename__ = "plot_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("plots.id"), nullable=False, unique=True
    )

    investment_score: Mapped[Optional[int]] = mapped_column(Integer)
    growth_potential: Mapped[Optional[str]] = mapped_column(Text)
    risk_level: Mapped[Optional[str]] = mapped_column(String)
    summary: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    plot: Mapped["Plot"] = relationship("Plot", back_populates="insight")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("plots.id", ondelete="CASCADE"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    plot: Mapped["Plot"] = relationship("Plot", back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    plot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("plots.id", ondelete="CASCADE"), nullable=False
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(768), nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    plot: Mapped["Plot"] = relationship("Plot")
