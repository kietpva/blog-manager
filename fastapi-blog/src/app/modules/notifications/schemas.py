from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationWS(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    type: str
    created_at: datetime

    @staticmethod
    def from_model(notification) -> "NotificationWS":
        return NotificationWS(
            id=notification.id,
            user_id=notification.user_id,
            title=notification.title,
            content=notification.content,
            type=notification.type,
            created_at=notification.created_at,
        )


class WSMessage(BaseModel):
    event: str
    data: dict
