import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ib_client import get_snapshot
from database import get_all_injections
from calculator import compute_returns

router = APIRouter()

PUSH_INTERVAL = 10  # seconds


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                snap = get_snapshot()
                rows = get_all_injections()
                injections = [(row.injected_on, row.amount_cny) for row in rows]
                ret = compute_returns(injections, snap.total_value_cny)

                payload = {
                    "snapshot": snap.model_dump(),
                    "returns": ret.model_dump(),
                }
                await websocket.send_text(json.dumps(payload, default=str))
            except Exception as e:
                await websocket.send_text(json.dumps({"error": str(e)}))

            await asyncio.sleep(PUSH_INTERVAL)
    except WebSocketDisconnect:
        pass
