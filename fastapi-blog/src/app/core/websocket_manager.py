from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """
    Manages active WebSocket connections for real-time features.

    This class maintains mappings between user IDs and their active WebSocket connections,
    allowing the application to push real-time notifications or updates to specific users.

    Key Responsibilities:
        - Track multiple WebSocket connections per user (e.g., multiple browser tabs/devices).
        - Safely add or remove connections on client connect/disconnect events.
        - Send JSON-encoded messages to all live sockets for a user.
    """

    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: str, websocket: WebSocket):
        """
        Register a new active WebSocket connection under the given user_id.

        Args:
            user_id (str): The external (auth) user identifier. Typically a unique string.
            websocket (WebSocket): The WebSocket connection instance.
        """
        self.connections[user_id].append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket):
        """
        Remove a previously registered WebSocket connection for a user.

        Args:
            user_id (str): The external (auth) user identifier.
            websocket (WebSocket): The WebSocket connection instance to remove.
        """
        self.connections[user_id].remove(websocket)

    async def send_notification(self, user_id: str, data: dict):
        """
        Send a JSON-encoded notification to all connected sockets for the given user.

        Args:
            user_id (str): The recipient user's ID.
            data (dict): The notification payload to send to the client(s).
        """
        for ws in self.connections.get(user_id, []):
            await ws.send_json(data)


manager = ConnectionManager()
