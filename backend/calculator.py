from datetime import date
import numpy as np
from scipy.optimize import brentq

from models import ReturnMetrics


def _xirr(cashflows: list[tuple[date, float]]) -> float | None:
    """
    Compute XIRR given a list of (date, amount) tuples.
    Negative amounts = money paid in (investments).
    Positive amounts = money received (current value = final cashflow).
    Returns annualized rate as a decimal (0.10 = 10%), or None if unsolvable.
    """
    if len(cashflows) < 2:
        return None

    dates, amounts = zip(*cashflows)
    t0 = dates[0]
    days = np.array([(d - t0).days / 365.0 for d in dates])
    amounts = np.array(amounts)

    def npv(rate):
        return np.sum(amounts / (1 + rate) ** days)

    try:
        return brentq(npv, -0.999, 100.0, maxiter=1000)
    except (ValueError, RuntimeError):
        return None


def compute_returns(
    injections: list[tuple[date, float]],  # (date, amount_cny)
    current_value_cny: float,
    as_of: date | None = None,
) -> ReturnMetrics:
    """
    injections: list of (injection_date, amount_in_cny), sorted ascending.
    current_value_cny: current total portfolio value in CNY.
    as_of: valuation date (defaults to today).
    """
    as_of = as_of or date.today()
    total_invested = sum(amt for _, amt in injections)

    total_return_pct = (
        (current_value_cny - total_invested) / total_invested * 100.0
        if total_invested > 0
        else 0.0
    )

    # Build XIRR cashflows: outflows (negative) at each injection, inflow at today
    cashflows: list[tuple[date, float]] = [
        (d, -amt) for d, amt in injections
    ]
    cashflows.append((as_of, current_value_cny))

    annualized = _xirr(cashflows)
    annualized_pct = annualized * 100.0 if annualized is not None else None

    return ReturnMetrics(
        total_return_pct=round(total_return_pct, 4),
        annualized_return_pct=round(annualized_pct, 4) if annualized_pct is not None else None,
        total_invested_cny=round(total_invested, 2),
        current_value_cny=round(current_value_cny, 2),
    )
