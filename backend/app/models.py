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

from .database import Base


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


class PlotImage(Base):
    __tablename__ = "plot_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plot_id: Mapped[int] = mapped_column(Integer, ForeignKey("plots.id"), nullable=False)

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
