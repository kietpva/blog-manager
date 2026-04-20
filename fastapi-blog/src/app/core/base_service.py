from sqlalchemy.orm import Session


class BaseService:
    """
    Base service providing common database session utilities.

    This class encapsulates shared transaction/session helpers,
    such as commit, rollback, and entity refresh, for use by
    service-layer classes in the application.

    Args:
        db (Session): The SQLAlchemy Session to operate on.
    """

    def __init__(self, db: Session):
        """
        Initialize the base service with the given SQLAlchemy session.

        Args:
            db (Session): An active SQLAlchemy session.
        """
        self.db = db

    def commit(self):
        """
        Commit the current transaction.
        """
        self.db.commit()

    def rollback(self):
        """
        Rollback the current transaction.
        """
        self.db.rollback()

    def refresh(self, entity):
        """
        Refresh the given entity from the database.

        Args:
            entity: The model instance to refresh.

        Returns:
            The refreshed entity instance.
        """
        self.db.refresh(entity)
        return entity

    def flush(self, entity):
        """
        Flush the current session to the database and return the entity.

        Args:
            entity: The model instance to be flushed.

        Returns:
            The entity instance after the session has been flushed.
        """

        self.db.flush()
        return entity

    def commit_and_refresh(self, entity):
        """
        Commit the current transaction, then refresh and return the entity.

        Args:
            entity: The model instance to refresh after commit.

        Returns:
            The refreshed entity instance.
        """
        self.db.commit()
        self.db.refresh(entity)
        return entity
