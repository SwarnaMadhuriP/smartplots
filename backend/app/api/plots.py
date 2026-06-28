from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Plot
from app.repositories.plot_search_repository import PlotSearchFilters, search_plots
from app.services.sorting_service import SortOption

router = APIRouter()


def plot_search_filters_from_query(
    search: str | None = Query(default=None, description="Keyword search alias"),
    keyword: str | None = Query(default=None),
    city: str | None = Query(default=None),
    state: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_area: float | None = Query(default=None, ge=0),
    max_area: float | None = Query(default=None, ge=0),
    zoning_type: str | None = Query(default=None),
    listing_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    road_access: bool | None = Query(default=None),
    water_access: bool | None = Query(default=None),
    electricity: bool | None = Query(default=None),
    sewer: bool | None = Query(default=None),
) -> PlotSearchFilters:
    return PlotSearchFilters(
        keyword=keyword or search,
        city=city,
        state=state,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
        zoning_type=zoning_type,
        listing_type=listing_type,
        status=status,
        road_access=road_access,
        water_access=water_access,
        electricity=electricity,
        sewer=sewer,
    )


@router.get("/plots")
def get_plots(
    filters: PlotSearchFilters = Depends(plot_search_filters_from_query),
    sort_by: SortOption = Query(default=SortOption.BEST_MATCH),
    db: Session = Depends(get_db),
):
    plots = search_plots(db, filters, sort_by=sort_by)
    return [plot.to_json_dict() for plot in plots]


@router.get("/plots/{plot_id}")
def get_plot(plot_id: int, db: Session = Depends(get_db)):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()

    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    return plot.to_json_dict()