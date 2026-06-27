from app.search import PlotSearchFilters, apply_plot_filters


class FakeExpression:
    def __init__(self, text: str) -> None:
        self.text = text

    def __repr__(self) -> str:
        return self.text


class FakeColumn:
    def __init__(self, name: str) -> None:
        self.name = name

    def ilike(self, pattern: str) -> FakeExpression:
        return FakeExpression(f"{self.name} ilike {pattern}")

    def is_(self, value: bool) -> FakeExpression:
        return FakeExpression(f"{self.name} is {value}")

    def __eq__(self, value: object) -> FakeExpression:  # type: ignore[override]
        return FakeExpression(f"{self.name} == {value}")

    def __ge__(self, value: object) -> FakeExpression:
        return FakeExpression(f"{self.name} >= {value}")

    def __le__(self, value: object) -> FakeExpression:
        return FakeExpression(f"{self.name} <= {value}")


class FakeQuery:
    def __init__(self) -> None:
        self.filters: list[object] = []

    def filter(self, *criteria: object) -> "FakeQuery":
        self.filters.extend(criteria)
        return self


def test_apply_plot_filters_uses_structured_filters(monkeypatch) -> None:
    class FakePlot:
        title = FakeColumn("title")
        description = FakeColumn("description")
        city = FakeColumn("city")
        state = FakeColumn("state")
        price = FakeColumn("price")
        area_acres = FakeColumn("area_acres")
        zoning_type = FakeColumn("zoning_type")
        listing_type = FakeColumn("listing_type")
        status = FakeColumn("status")
        road_access = FakeColumn("road_access")
        water_access = FakeColumn("water_access")
        electricity = FakeColumn("electricity")
        sewer = FakeColumn("sewer")
        nearby_landmarks = FakeColumn("nearby_landmarks")
        ideal_for = FakeColumn("ideal_for")
        risk_notes = FakeColumn("risk_notes")

    monkeypatch.setattr("app.search.Plot", FakePlot)
    monkeypatch.setattr("app.search.or_", lambda *criteria: ("or", criteria))

    filters = PlotSearchFilters(
        city="Austin",
        min_price=50_000,
        max_price=150_000,
        road_access=True,
        keyword="lake",
    )
    query = apply_plot_filters(FakeQuery(), filters)
    rendered = repr(query.filters)

    assert "city ilike %Austin%" in rendered
    assert "price >= 50000" in rendered
    assert "price <= 150000" in rendered
    assert "road_access is True" in rendered
    assert "lake" in rendered
