from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Plot(Base):
    __tablename__ = "plots"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)

    price = Column(Float, nullable=False)
    area_acres = Column(Float, nullable=False)

    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String)

    latitude = Column(Float)
    longitude = Column(Float)

    zoning_type = Column(String)
    listing_type = Column(String, default="sale")
    status = Column(String, default="available")

    road_access = Column(Boolean, default=False)
    water_access = Column(Boolean, default=False)
    electricity = Column(Boolean, default=False)
    sewer = Column(Boolean, default=False)

    nearby_landmarks = Column(Text)
    ideal_for = Column(Text)
    risk_notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    images = relationship(
        "PlotImage", back_populates="plot", cascade="all, delete-orphan"
    )
    insight = relationship(
        "PlotInsight",
        back_populates="plot",
        uselist=False,
        cascade="all, delete-orphan",
    )


class PlotImage(Base):
    __tablename__ = "plot_images"

    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(Integer, ForeignKey("plots.id"), nullable=False)

    image_url = Column(Text, nullable=False)
    alt_text = Column(String)
    is_primary = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    plot = relationship("Plot", back_populates="images")


class PlotInsight(Base):
    __tablename__ = "plot_insights"

    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(Integer, ForeignKey("plots.id"), nullable=False, unique=True)

    investment_score = Column(Integer)
    growth_potential = Column(Text)
    risk_level = Column(String)
    summary = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    plot = relationship("Plot", back_populates="insight")
