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

REFRESH_INTERVAL = 60   # seconds between IB data refreshes
SNAPSHOT_TIMEOUT = 90   # seconds before giving up on a single IB round-trip

_payload: Optional[str] = None   # pre-serialised JSON string (None = not ready yet)
_clients: set[WebSocket] = set()


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
    global _payload

    # Lazy imports to avoid circular deps at module load time
    from ib_client import get_snapshot
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
            logger.info("Snapshot refreshed (usdcnh=%.4f)", snap.usdcnh_rate)
            await _broadcast(_payload)

        except asyncio.TimeoutError:
            logger.error("Snapshot timed out after %ds — forcing IB disconnect", SNAPSHOT_TIMEOUT)
            try:
                from ib_client import _ib
                _ib.disconnect()
            except Exception:
                pass

        except Exception as exc:
            logger.error("Snapshot refresh failed: %s", exc)
            err = json.dumps({"error": str(exc)})
            await _broadcast(err)

        await asyncio.sleep(REFRESH_INTERVAL)
