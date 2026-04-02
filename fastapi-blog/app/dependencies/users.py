from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.common import get_db
from app.modules.users.repositories import UserRepository
from app.modules.users.services import UserService


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)
