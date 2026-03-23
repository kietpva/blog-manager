import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BaseModel


class Post(Base, BaseModel):
    __tablename__ = "posts"
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)

    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
