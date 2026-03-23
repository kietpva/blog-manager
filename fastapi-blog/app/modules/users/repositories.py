from sqlalchemy.orm import Session
from app.modules.users.models import User
from pydantic import BaseModel


class UserRepository:
    def __init__(self, db: Session):
        """
        Initialize the UserRepository with a database session.
        SQLAlchemy session for database operations.
        """
        self.db = db

    def create(self, user: User) -> User:
        """
        Add a new user to the database.
        If the user already exists.
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_auth_id(self, auth_id: str) -> User | None:
        """
        Retrieve a user by their authentication ID.
        The user instance if found, otherwise None.
        """
        return self.db.query(User).filter(User.auth_id == auth_id).one_or_none()

    def get_by_user_id(self, user_id: str) -> User | None:
        """
        Retrieve a user by their internal user ID.
        The user instance if found, otherwise None.
        """
        return self.db.query(User).filter(User.id == user_id).one_or_none()

    def get_list(self) -> list[User]:
        """
        Retrieve a list of all users.
        """
        return self.db.query(User).all()

    def update(self, user: User, payload: BaseModel) -> User:
        """
        Update an existing user's data.
        The updated user instance.
        """
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User):
        """
        Delete a user from the database.
        """
        self.db.delete(user)
        self.db.commit()
