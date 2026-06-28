from pydantic import BaseModel


class CompareRequest(BaseModel):
    plot_ids: list[int]
    goal: str | None = None


class ComparePlotProfile(BaseModel):
    plot_id: int
    award_label: str
    suitability_score: int
    key_tradeoff: str


class ComparisonResponse(BaseModel):
    overall_recommendation: str
    profiles: list[ComparePlotProfile]
    summary_points: list[str]
