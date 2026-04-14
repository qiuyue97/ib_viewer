from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from cache import register, unregister, get_cached

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    register(websocket)
    try:
        # Send the latest cached snapshot immediately — no waiting for IB
        cached = get_cached()
        if cached:
            await websocket.send_text(cached)

        # Keep the connection alive; the background loop pushes updates
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        unregister(websocket)
