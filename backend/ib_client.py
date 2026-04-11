import os
from datetime import datetime, timezone

from ib_insync import IB, Forex, util
from models import AccountSnapshot, Position

util.startLoop()  # allows ib_insync to work inside asyncio event loop

_ib = IB()


def _ensure_connected():
    if not _ib.isConnected():
        _ib.connect(
            host=os.getenv("IB_HOST", "127.0.0.1"),
            port=int(os.getenv("IB_PORT", "4002")),
            clientId=int(os.getenv("IB_CLIENT_ID", "1")),
            readonly=True,
        )


def _get_usdcnh_rate() -> tuple[float, str]:
    """Returns (rate, iso_timestamp). Rate is CNY per 1 USD."""
    pair = Forex("USDCNH")
    _ib.qualifyContracts(pair)
    ticker = _ib.reqMktData(pair, "", False, False)
    _ib.sleep(1)  # wait for market data
    rate = ticker.last or ticker.close or 0.0
    _ib.cancelMktData(pair)
    ts = datetime.now(timezone.utc).isoformat()
    return float(rate), ts


def get_snapshot() -> AccountSnapshot:
    _ensure_connected()

    account_id = os.getenv("IB_ACCOUNT_ID", "")

    # --- account values ---
    account_values = {
        v.tag: v
        for v in _ib.accountValues()
        if v.currency == "USD" and (not account_id or v.account == account_id)
    }
    cash_usd = float(account_values.get("CashBalance", type("x", (), {"value": "0"})()).value)

    # --- exchange rate ---
    usdcnh_rate, ts = _get_usdcnh_rate()
    cash_cny = cash_usd * usdcnh_rate

    # --- positions ---
    raw_positions = _ib.positions(account=account_id if account_id else "")
    positions: list[Position] = []

    for pos in raw_positions:
        contract = pos.contract
        ticker = _ib.reqMktData(contract, "", False, False)
        _ib.sleep(0.5)
        market_price = ticker.last or ticker.close or pos.avgCost
        _ib.cancelMktData(contract)

        market_value = pos.position * market_price
        if contract.currency == "USD":
            market_value_cny = market_value * usdcnh_rate
        else:
            market_value_cny = market_value  # already CNY or unknown

        positions.append(Position(
            symbol=contract.symbol,
            sec_type=contract.secType,
            currency=contract.currency,
            quantity=pos.position,
            avg_cost=pos.avgCost,
            market_price=market_price,
            market_value=market_value,
            market_value_cny=market_value_cny,
        ))

    total_value_cny = cash_cny + sum(p.market_value_cny for p in positions)

    return AccountSnapshot(
        cash_usd=cash_usd,
        cash_cny=cash_cny,
        usdcnh_rate=usdcnh_rate,
        positions=positions,
        total_value_cny=total_value_cny,
        rate_timestamp=ts,
    )
