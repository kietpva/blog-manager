from fastapi import WebSocket

from src.app.core.exceptions import UnauthorizedError
from src.app.core.jwt import verify_auth_token


async def verify_ws(websocket: WebSocket) -> dict:
    """
    Verifies the JWT token provided in the query parameters of the WebSocket connection.

    This function extracts the "token" from the websocket's query parameters and attempts
    to validate it using the application's JWT verification logic. If the token is missing
    or invalid, the websocket connection is gracefully closed with code 1008 and an
    UnauthorizedError is raised.

    Args:
        websocket (WebSocket): The WebSocket connection attempting authentication.

    Returns:
        dict: The JWT payload if the token is valid.

    Raises:
        UnauthorizedError: If the token is missing or invalid.
    """

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        raise UnauthorizedError(message="Missing token")

    try:
        payload = verify_auth_token(token)
        return payload

    except Exception:
        await websocket.close(code=1008)
        raise UnauthorizedError(message="Invalid token")
