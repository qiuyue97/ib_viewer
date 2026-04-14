from datetime import date
from pydantic import BaseModel, ConfigDict


class Position(BaseModel):
    symbol: str
    sec_type: str        # STK, FUT, OPT, CASH, etc.
    currency: str
    quantity: float
    avg_cost: float      # average cost in position currency
    market_price: float
    market_value: float  # in position currency
    market_value_cny: float


class AccountSnapshot(BaseModel):
    cash_usd: float        # actual USD cash held
    cash_cnh: float        # actual CNH (offshore CNY) cash held
    cash_cny: float        # total cash in CNY = cash_cnh + cash_usd * rate
    usdcnh_rate: float
    positions: list[Position]
    total_value_cny: float
    rate_timestamp: str   # ISO datetime string


class CapitalInjectionIn(BaseModel):
    amount_cny: float
    injected_on: date
    note: str = ""


class CapitalInjection(CapitalInjectionIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ReturnMetrics(BaseModel):
    total_return_pct: float
    annualized_return_pct: float | None  # None if < 1 day of data
    total_invested_cny: float
    current_value_cny: float
