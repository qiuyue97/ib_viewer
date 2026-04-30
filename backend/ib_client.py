import logging
import math
import os
from datetime import datetime, timezone

from ib_insync import IB, Forex, util
from models import AccountSnapshot, Position
from options_utils import format_option_symbol, calculate_market_value_with_multiplier, get_option_multiplier

util.startLoop()

logger = logging.getLogger(__name__)

_SUPPRESSED_IB_CODES = frozenset({354, 10091})

class _IBErrorFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return not any(f'Error {code},' in msg for code in _SUPPRESSED_IB_CODES)

_ib_filter = _IBErrorFilter()
for _n in ('ib_insync', 'ib_insync.wrapper', 'ib_insync.ib', 'ib_insync.client'):
    logging.getLogger(_n).addFilter(_ib_filter)

_ib = IB()
_usdcnh_contract: Forex | None = None


def _on_ib_error(reqId: int, errorCode: int, errorString: str, contract) -> None:
    if errorCode == 1100:
        logger.warning("IB connectivity lost (1100) — disconnecting to force clean reconnect")
        _ib.disconnect()
    elif errorCode == 1102:
        # "data maintained" means subscriptions survived, but ib_insync's internal
        # pending-request queue may be stale; disconnect to reset it cleanly.
        logger.warning("IB connectivity restored (1102) — reconnecting to reset client state")
        _ib.disconnect()


_ib.errorEvent += _on_ib_error


def _first_valid_price(*values) -> float | None:
    """Return first strictly-positive, non-NaN value, or None if all invalid.

    Intended for market prices only. IB uses -1 to signal "unavailable" and
    0 as a default placeholder — both are rejected here.
    """
    for v in values:
        try:
            f = float(v)
            if not math.isnan(f) and f > 0.0:
                return f
        except (TypeError, ValueError):
            pass
    return None


def _ensure_connected():
    if not _ib.isConnected():
        _ib.connect(
            host=os.getenv("IB_HOST", "127.0.0.1"),
            port=int(os.getenv("IB_PORT", "4002")),
            clientId=int(os.getenv("IB_CLIENT_ID", "1")),
            readonly=True,
        )
        # Type 4 = delayed frozen (free). During market hours: ~15-20 min delayed.
        # After market close / weekends: returns last known ("frozen") price.
        # Confirmed from wrapper.py: delayed tick types (68/75) write to the same
        # ticker.last / ticker.close fields as real-time tick types (4/9).
        _ib.reqMarketDataType(4)


def _get_usdcnh_rate() -> tuple[float, str]:
    """Returns (rate, iso_timestamp). Rate is CNY per 1 USD."""
    global _usdcnh_contract
    if _usdcnh_contract is None:
        _usdcnh_contract = Forex("USDCNH")
        _ib.qualifyContracts(_usdcnh_contract)

    # Try snapshot tick data first (works during market hours).
    [ticker] = _ib.reqTickers(_usdcnh_contract)
    rate = _first_valid_price(
        (ticker.bid + ticker.ask) / 2 if ticker.bid and ticker.ask else None,
        ticker.midpoint(),
        ticker.marketPrice(),
        ticker.close,
    )

    if rate is None:
        # Fallback: historical MIDPOINT data — free for Forex, always has a
        # close price even on weekends (last known session close).
        bars = _ib.reqHistoricalData(
            _usdcnh_contract,
            endDateTime="",
            durationStr="2 D",
            barSizeSetting="1 day",
            whatToShow="MIDPOINT",
            useRTH=False,
            keepUpToDate=False,
        )
        if bars:
            rate = bars[-1].close

    ts = datetime.now(timezone.utc).isoformat()
    return rate or 0.0, ts


def _get_cash_balances(account_id: str) -> tuple[float, float]:
    """Return (cash_usd, cash_cnh) from per-currency CashBalance in accountValues.

    accountValues() is populated at connect time via reqAccountUpdatesMulti for
    each sub-account (confirmed in ib_insync connectAsync source). It provides
    CashBalance per currency — unlike accountSummary() which only returns the
    total converted to the base currency (USD).
    """
    values = _ib.accountValues(account=account_id)
    cash_usd = 0.0
    cash_cnh = 0.0
    for v in values:
        if v.tag != "CashBalance":
            continue
        try:
            val = float(v.value)
        except ValueError:
            continue
        if v.currency == "USD":
            cash_usd = val
        elif v.currency == "CNH":
            cash_cnh = val
    return cash_usd, cash_cnh


def get_snapshot() -> AccountSnapshot:
    _ensure_connected()

    account_id = os.getenv("IB_ACCOUNT_ID", "")

    # --- per-currency cash balances (supports negative / margin balances) ---
    cash_usd, cash_cnh = _get_cash_balances(account_id)

    # --- exchange rate ---
    usdcnh_rate, ts = _get_usdcnh_rate()

    # total cash in CNY: actual CNH held + USD converted (works correctly when
    # cash_usd is negative, e.g. -100 USD × 7.25 = -725 CNY)
    cash_cny = cash_cnh + cash_usd * usdcnh_rate

    # --- positions ---
    raw_positions = _ib.positions(account=account_id if account_id else "")

    # Request market data for all contracts simultaneously, then wait once.
    # Positions from IB often lack exchange; SMART covers all US-listed contracts.
    contracts = [pos.contract for pos in raw_positions]
    for c in contracts:
        if not c.exchange:
            c.exchange = "SMART"
    tickers = _ib.reqTickers(*contracts)

    positions: list[Position] = []
    for pos, ticker in zip(raw_positions, tickers):
        contract = pos.contract
        # Use _first_valid_price here: IB marks unavailable prices as -1 or 0,
        # which are meaningless for positions and must be rejected.
        market_price = _first_valid_price(
            (ticker.bid + ticker.ask) / 2 if ticker.bid and ticker.ask else None,
            ticker.last,
            ticker.close,
        )
        if market_price is None:
            # avgCost for options is per-contract (already ×multiplier); divide back
            # to per-share so it stays consistent with ticker prices.
            if contract.secType == "OPT":
                market_price = pos.avgCost / get_option_multiplier(contract)
            else:
                market_price = pos.avgCost
        if contract in _ib.tickers():
            _ib.cancelMktData(contract)

        # 根据合约类型选择符号格式
        if contract.secType == "OPT":
            symbol = format_option_symbol(contract)
        else:
            symbol = contract.symbol  # 股票等保持原样

        # 根据合约类型计算市值
        if contract.secType == "OPT":
            market_value = calculate_market_value_with_multiplier(
                pos.position, market_price, contract
            )
        else:
            market_value = pos.position * market_price
        if contract.currency == "USD":
            market_value_cny = market_value * usdcnh_rate
        else:
            market_value_cny = market_value

        positions.append(Position(
            symbol=symbol,
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
        cash_cnh=cash_cnh,
        cash_cny=cash_cny,
        usdcnh_rate=usdcnh_rate,
        positions=positions,
        total_value_cny=total_value_cny,
        rate_timestamp=ts,
    )