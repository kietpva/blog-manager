import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import certifi
from fastapi import BackgroundTasks
from sqlalchemy.exc import IntegrityError

from src.app.core.base_service import BaseService
from src.app.core.config import settings
from src.app.core.constants import SortOrder
from src.app.core.decorators.retry import RetryFactory
from src.app.core.exceptions import (
    BadRequestError,
    NotFoundError,
)
from src.app.core.permissions import check_permission
from src.app.modules.users.models import User
from src.app.modules.users.repositories import UserRepository
from src.app.modules.users.schemas import (
    UserCreate,
    UserUpdate,
    UserUpdateByWebhooks,
)
from src.app.utils.helpers import apply_partial_update
from src.app.utils.pagination import PaginationInfo


class UserService(BaseService):
    """
    Service layer for user-related business logic.

    Provides methods for creating users, retrieving user details, updating user information,
    and administrative user updates. Delegates database operations to the UserRepository.
    Handles application exceptions and ensures appropriate error handling for user actions.
    """

    def __init__(self, repo: UserRepository) -> None:
        """
        Initialize the UserService with a UserRepository instance.

        Args:
            repo (UserRepository): The repository used for user database operations.
        """
        super().__init__(repo.db)
        self.repo = repo
        self.smtp_server = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.email = settings.SMTP_FROM
        self.password = settings.SMTP_FROM

    @RetryFactory.service()
    def create(
        self,
        payload: UserCreate,
        background_tasks=BackgroundTasks,
    ) -> User:
        """
        Create a new user in the system.

        Args:
            payload (UserCreate): The data required to create a new user.

        Returns:
            User: The created or already-existing user.

        Raises:
            AppError: If attempting to create a duplicate user.
        """
        existing_user = self.repo.get_by_auth_id(payload.auth_id)

        if existing_user:
            return existing_user

        user = User(
            auth_id=payload.auth_id,
            email=str(payload.email),
            first_name=payload.first_name,
            last_name=payload.last_name,
            is_active=payload.is_active,
        )

        try:
            self.repo.create(user)
            result = self.commit_and_refresh(user)

            background_tasks.add_task(
                self.send_email,
                to_email=user.email,
                subject="Welcome to Blog Manager",
                body=f"<h2>Welcome {user.email} 🎉</h2>",
            )

            return result

        except IntegrityError:
            raise BadRequestError(message="User already exists")

    @RetryFactory.service()
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
    ):
        """
        Sends an email to the specified recipient.

        Args:
            to_email (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The HTML body content of the email.

        Raises:
            smtplib.SMTPException: If sending the email fails.
        """

        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))
        context = ssl.create_default_context(cafile=certifi.where())

        try:
            if settings.SMTP_PORT == 587:
                with smtplib.SMTP(
                    host=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    timeout=10,
                ) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()

                    server.login(
                        user=settings.SMTP_USERNAME,
                        password=settings.SMTP_PASSWORD,
                    )

                    server.sendmail(
                        from_addr=self.email,
                        to_addrs=to_email,
                        msg=msg.as_string(),
                    )
            else:
                with smtplib.SMTP_SSL(
                    host=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    context=context,
                    timeout=10,
                ) as server:
                    server.login(
                        user=settings.SMTP_USERNAME,
                        password=settings.SMTP_PASSWORD,
                    )

                    server.sendmail(
                        from_addr=self.email,
                        to_addrs=to_email,
                        msg=msg.as_string(),
                    )
            logging.info("Email sent!")

        except smtplib.SMTPException:
            logging.exception("Failed to send email")
            raise

    @RetryFactory.service()
    def get_by_id(self, user_id: str) -> User:
        """
        Retrieve a user by their ID.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            User: The user object if found.

        Raises:
            NotFoundException: If no such user exists.
        """
        user = self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError(message="User not found")

        return user

    @RetryFactory.service()
    def list(
        self,
        limit: int,
        offset: int,
        order_by: SortOrder = SortOrder.NEWEST,
        search: str | None = None,
    ) -> tuple[PaginationInfo, list[User]]:
        """
        List users with pagination support.

        Args:
            limit (int): Maximum users to return.
            offset (int): Number of records to skip.

        Returns:
            tuple[PaginationInfo, list[User]]: Pagination metadata and user list.
        """

        return self.repo.list(limit, offset, order_by=order_by, search=search)

    @RetryFactory.service()
    def partial_update(
        self,
        *,
        payload: UserUpdate,
        user_id: str,
        current_user: User,
    ) -> User:
        """
        Partially update a user's own profile.

        Users may only update their own record. Ownership validation is enforced
        by check_permission.

        Args:
            payload (UserUpdate): Fields to update.
            user_id (str): The user record to modify.
            current_user (User): Authenticated user attempting the update.

        Returns:
            User: Updated user object.

        Raises:
            AppError: If the user does not have permission to update this record.
        """
        check_permission(current_user=current_user, owner_id=user_id)

        user = self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError(message="User not found")

        apply_partial_update(instance=user, data=payload.model_dump(exclude_unset=True))

        return self.commit_and_refresh(user)

    def update_by_webhooks(self, auth_id: str, payload: UserUpdateByWebhooks) -> User:
        user = self.repo.get_by_auth_id(auth_id=auth_id)

        self.partial_update(payload=payload, user_id=user.id, current_user=user)
