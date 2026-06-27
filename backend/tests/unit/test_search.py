from app.search import PlotSearchFilters, apply_plot_filters, extract_query_filters


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


def test_extract_query_filters_handles_price_city_and_utilities() -> None:
    filters = extract_query_filters(
        "plots under 100k in Austin with water and electricity",
        PlotSearchFilters(keyword="plots under 100k in Austin with water and electricity"),
    )

    assert filters.keyword is None
    assert filters.max_price == 100_000
    assert filters.city == "Austin"
    assert filters.water_access is True
    assert filters.electricity is True


def test_extract_query_filters_treats_residential_area_as_zoning() -> None:
    filters = extract_query_filters(
        "can you show me plots in residential area",
        PlotSearchFilters(keyword="can you show me plots in residential area"),
    )

    assert filters.keyword is None
    assert filters.city is None
    assert filters.zoning_type == "Residential"
