from sqlalchemy.orm import Session
from app.modules.users.models import User
from pydantic import BaseModel


class UserRepository:
    def __init__(self, db: Session):
        """
        Initialize the UserRepository with a SQLAlchemy database session.

        Args:
            db (Session): The SQLAlchemy database session instance.
        """
        self.db = db

    def create(self, user: User) -> User:
        """
        Add a new user to the database.

        Args:
            user (User): The user instance to be added.

        Returns:
            User: The newly added user, refreshed from the database.
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_auth_id(self, auth_id: str) -> User | None:
        """
        Retrieve a user by their authentication ID.

        Args:
            auth_id (str): The authentication ID of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return self.db.query(User).filter(User.auth_id == auth_id).one_or_none()

    def get_by_user_id(self, user_id: str) -> User | None:
        """
        Retrieve a user by their user ID.

        Args:
            user_id (str): The unique user ID.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return self.db.query(User).filter(User.id == user_id).one_or_none()

    def get_list(self) -> list[User]:
        """
        Retrieve a list of all users from the database.

        Returns:
            list[User]: A list of all user instances.
        """
        return self.db.query(User).all()

    def update(self, user: User, payload: BaseModel) -> User:
        """
        Update the given user with values from the payload.

        Args:
            user (User): The user instance to update.
            payload (BaseModel): The update data (Pydantic model) with new field values.

        Returns:
            User: The updated user instance.
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
        Delete the specified user from the database.

        Args:
            user (User): The user instance to delete.
        """
        self.db.delete(user)
        self.db.commit()
