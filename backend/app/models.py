from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .database import Base, engine


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

        risk_text = f"{self.risk_notes or ''} {self.description or ''}".lower()

        missing_utilities = sum(
            1
            for value in [
                self.road_access,
                self.water_access,
                self.electricity,
                getattr(self, "sewer", False),
            ]
            if not value
        )

        high_risk_terms = ["flood", "hazard", "contamination", "legal", "dispute"]
        medium_risk_terms = ["limited", "restriction", "noise", "competition", "soil"]

        if any(term in risk_text for term in high_risk_terms) or missing_utilities >= 3:
            return "High"

        if any(term in risk_text for term in medium_risk_terms) or missing_utilities >= 2:
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

        desc_text = f"{self.description or ''} {self.nearby_landmarks or ''}".lower()

        high_terms = [
            "downtown",
            "rapidly growing",
            "growth corridor",
            "suburb",
            "highway",
            "tech hub",
            "near airport",
            "development",
            "commercial",
            "mixed use",
            "expansion",
        ]

        low_terms = [
            "flood",
            "hazard",
            "restricted",
            "remote",
            "declining",
            "poor access",
        ]

        if any(term in desc_text for term in high_terms):
            return "High"

        if any(term in desc_text for term in low_terms):
            return "Low"

        missing_utilities = sum(
            1
            for value in [
                self.road_access,
                self.water_access,
                self.electricity,
                getattr(self, "sewer", False),
            ]
            if not value
        )

        if missing_utilities >= 3:
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
            "rawPrice": self.price,
            "acres": f"{self.area_acres} Acres",
            "rawAcres": self.area_acres,
            "zone": self.zoning_type or "General",
            "matchScore": self.computed_match_score,
            "investmentScore": self.computed_match_score,
            "appreciation": self.computed_appreciation,
            "rentalDemand": self.computed_rental_demand,
            "liquidity": self.computed_liquidity,
            "riskLevel": self.computed_risk_level,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "reasons": reasons[:3],
            "highlights": (
                [item.strip() for item in self.ideal_for.split(",")]
                if self.ideal_for
                else ["Suitable for residential or investment use"]
            ),
        }


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
