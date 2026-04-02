from datetime import datetime

from sqlalchemy import event

from app.db.base import BaseModel


@event.listens_for(BaseModel, "before_update", propagate=True)
def update_timestamp(mapper, connection, target):
    target.updated_at = datetime.now()
