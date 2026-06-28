from pydantic import BaseModel, Field
from app.search import PlotSearchFilters
from app.sorting import SortOption
from typing import Any

class SmartSearchRequest(BaseModel):
    query: str


class SearchFiltersPayload(BaseModel):
    keyword: str | None = None
    city: str | None = None
    state: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_area: float | None = None
    max_area: float | None = None
    zoning_type: str | None = None
    listing_type: str | None = None
    status: str | None = None
    road_access: bool | None = None
    water_access: bool | None = None
    electricity: bool | None = None
    sewer: bool | None = None

    def to_filters(self, keyword: str | None = None) -> PlotSearchFilters:
        return PlotSearchFilters(
            keyword=keyword if keyword is not None else self.keyword,
            city=self.city,
            state=self.state,
            min_price=self.min_price,
            max_price=self.max_price,
            min_area=self.min_area,
            max_area=self.max_area,
            zoning_type=self.zoning_type,
            listing_type=self.listing_type,
            status=self.status,
            road_access=self.road_access,
            water_access=self.water_access,
            electricity=self.electricity,
            sewer=self.sewer,
        )

    def active_dict(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in self.model_dump().items()
            if value not in (None, "")
        }


class UnifiedSearchRequest(BaseModel):
    query: str = ""
    filters: SearchFiltersPayload = Field(default_factory=SearchFiltersPayload)
    sort_by: SortOption = SortOption.BEST_MATCH