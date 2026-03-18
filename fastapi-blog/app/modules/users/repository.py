from app.modules.users.model import User
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import AppError, ErrorCode, StatusCode
from app.modules.users.schema import UserCreate


class UserRepository:
    def __init__(self, db):
        self.db = db

    def create(self, payload: UserCreate) -> User:
        user = User(
            auth_id=payload.auth_id,
            email=str(payload.email),
            first_name=payload.first_name,
            last_name=payload.last_name,
        )

        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()

            existing = self.get_by_auth_id(payload.auth_id) or (
                self.get_by_email(str(payload.email)) if payload.email else None
            )
            if existing:
                raise AppError(
                    code=ErrorCode.bad_request,
                    message="User already exists",
                    status_code=StatusCode.bad_request,
                )

            raise AppError(
                code=ErrorCode.bad_request,
                message="Invalid user data",
                status_code=StatusCode.bad_request,
            )
        except SQLAlchemyError:
            self.db.rollback()
            raise AppError(
                code=ErrorCode.internal_server_error,
                message="Failed to create user",
                status_code=StatusCode.internal_server_error,
            )

        return user

    def get_by_auth_id(self, auth_id) -> User | None:
        try:
            return self.db.query(User).filter_by(auth_id=auth_id).one_or_none()
        except SQLAlchemyError:
            raise AppError(
                code=ErrorCode.internal_server_error,
                message="Failed to fetch user by auth_id",
                status_code=StatusCode.internal_server_error,
            )

    def get_by_email(self, email) -> User | None:
        try:
            return self.db.query(User).filter_by(email=email).one_or_none()
        except SQLAlchemyError:
            raise AppError(
                code=ErrorCode.internal_server_error,
                message="Failed to fetch user by email",
                status_code=StatusCode.internal_server_error,
            )

    def get_all(self) -> list[User]:
        try:
            return self.db.query(User).all()
        except SQLAlchemyError:
            raise AppError(
                code=ErrorCode.internal_server_error,
                message="Failed to fetch users",
                status_code=StatusCode.internal_server_error,
            )
