import pytest
from datetime import date
from calculator import compute_returns


def test_simple_positive_return():
    injections = [(date(2024, 1, 1), 100_000.0)]
    result = compute_returns(injections, current_value_cny=110_000.0, as_of=date(2025, 1, 1))
    assert result.total_return_pct == 10.0
    assert result.annualized_return_pct is not None
    assert 9.5 < result.annualized_return_pct < 10.5


def test_zero_investment():
    result = compute_returns([], current_value_cny=0.0, as_of=date(2025, 1, 1))
    assert result.total_return_pct == 0.0
    assert result.annualized_return_pct is None


def test_multiple_injections():
    injections = [
        (date(2024, 1, 1), 100_000.0),
        (date(2024, 7, 1), 50_000.0),
    ]
    result = compute_returns(injections, current_value_cny=165_000.0, as_of=date(2025, 1, 1))
    assert result.total_invested_cny == 150_000.0
    assert result.total_return_pct == pytest.approx(10.0, abs=0.01)
