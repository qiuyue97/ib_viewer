"""Background snapshot cache.

One asyncio task refreshes the IB snapshot every REFRESH_INTERVAL seconds and
broadcasts the result to all connected WebSocket clients.  New clients receive
the latest cached payload immediately upon connection instead of waiting for
the next IB round-trip.
"""
import asyncio
import json
import logging
from typing import Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)

REFRESH_INTERVAL = 60        # seconds between IB data refreshes
SNAPSHOT_TIMEOUT = 90        # seconds before giving up on a single IB round-trip
RESET_AFTER_FAILURES = 3     # recreate IB object after this many consecutive timeouts

_payload: Optional[str] = None   # pre-serialised JSON string (None = not ready yet)
_clients: set[WebSocket] = set()
_consecutive_failures: int = 0


# ---------------------------------------------------------------------------
# Client registry (called by the WebSocket router)
# ---------------------------------------------------------------------------

def register(ws: WebSocket) -> None:
    _clients.add(ws)


def unregister(ws: WebSocket) -> None:
    _clients.discard(ws)


def get_cached() -> Optional[str]:
    """Return the latest serialised payload, or None if not yet ready."""
    return _payload


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _broadcast(msg: str) -> None:
    dead: set[WebSocket] = set()
    for ws in _clients:
        try:
            await ws.send_text(msg)
        except Exception:
            dead.add(ws)
    _clients.difference_update(dead)


# ---------------------------------------------------------------------------
# Background refresh loop — start once via asyncio.create_task()
# ---------------------------------------------------------------------------

async def refresh_loop() -> None:
    global _payload, _consecutive_failures

    # Lazy imports to avoid circular deps at module load time
    from ib_client import get_snapshot, reset_ib_client
    from database import get_all_injections
    from calculator import compute_returns

    while True:
        try:
            # Run the blocking IB call in a thread so the event loop stays
            # responsive to error callbacks (1100/1102). The timeout ensures
            # we never hang permanently if reqTickers() never returns.
            snap = await asyncio.wait_for(
                asyncio.to_thread(get_snapshot),
                timeout=SNAPSHOT_TIMEOUT,
            )
            rows = get_all_injections()
            injections = [(r.injected_on, r.amount_cny) for r in rows]
            ret = compute_returns(injections, snap.total_value_cny)

            data = {
                "snapshot": snap.model_dump(),
                "returns": ret.model_dump(),
            }
            _payload = json.dumps(data, default=str)
            _consecutive_failures = 0
            logger.info("Snapshot refreshed (usdcnh=%.4f)", snap.usdcnh_rate)
            await _broadcast(_payload)

        except asyncio.TimeoutError:
            _consecutive_failures += 1
            logger.error(
                "Snapshot timed out after %ds (failure %d/%d)",
                SNAPSHOT_TIMEOUT, _consecutive_failures, RESET_AFTER_FAILURES,
            )
            if _consecutive_failures >= RESET_AFTER_FAILURES:
                logger.warning("Recreating IB client after %d consecutive failures", _consecutive_failures)
                reset_ib_client()
                _consecutive_failures = 0
            else:
                try:
                    from ib_client import _ib
                    _ib.disconnect()
                except Exception:
                    pass

        except Exception as exc:
            _consecutive_failures += 1
            logger.error("Snapshot refresh failed: %s", exc)
            err = json.dumps({"error": str(exc)})
            await _broadcast(err)

        await asyncio.sleep(REFRESH_INTERVAL)
