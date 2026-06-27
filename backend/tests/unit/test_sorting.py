from app.sorting import SortOption, sort_plot_dicts


def test_sort_plot_dicts_by_price_and_ai_score() -> None:
    plots = [
        {"id": 1, "rawPrice": 200_000, "aiInvestmentScore": 7},
        {"id": 2, "rawPrice": 100_000, "aiInvestmentScore": 9},
        {"id": 3, "rawPrice": 150_000, "aiInvestmentScore": 6},
    ]

    assert [p["id"] for p in sort_plot_dicts(plots, SortOption.PRICE_ASC)] == [
        2,
        3,
        1,
    ]
    assert [
        p["id"] for p in sort_plot_dicts(plots, SortOption.AI_INVESTMENT_SCORE)
    ] == [2, 1, 3]


def test_best_match_preserves_existing_order() -> None:
    plots = [{"id": 3}, {"id": 1}, {"id": 2}]

    assert sort_plot_dicts(plots, SortOption.BEST_MATCH) == plots
