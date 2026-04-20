from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.app.core.websocket_manager import manager
from src.app.dependencies.auth_ws import verify_ws

router = APIRouter()


@router.websocket("/ws/notifications")
async def notification_ws(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.

    This endpoint authenticates incoming WebSocket connections using a JWT token
    (sent via query parameters), registers the connection with the application's
    connection manager under the authenticated user's ID, and keeps the socket open
    to receive push notification events for that user.

    On connect:
        - Authenticates the user by verifying the JWT token.
        - Accepts the WebSocket connection if valid.
        - Registers the connection in the manager for pushing notification events.

    On disconnect:
        - Removes the connection from the connection manager.

    The WebSocket expects and discards any incoming client messages (i.e., "ping"-style),
    as push data is server-initiated only.

    Args:
        websocket (WebSocket): The active WebSocket connection instance.

    Protocol:
        - Path: /ws/notifications
        - JWT should be supplied as "token" query param.
        - Closes with code 1008 (Policy Violation) if unauthorized.
    """
    await websocket.accept()

    try:
        payload = await verify_ws(websocket)

        user_id = payload.get("sub")

        if not user_id:
            await websocket.close(code=1008)
            return

        await manager.connect(user_id, websocket)

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
