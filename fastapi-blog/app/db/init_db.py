from app.db.base import Base
from app.db.session import engine
from app.modules.users.model import User  # noqa: F401 - ensure model is imported


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
