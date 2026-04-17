import logging
import random
import smtplib

import requests
from sqlalchemy.exc import OperationalError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
)

logger = logging.getLogger(__name__)


def custom_wait(retry_state):
    """
    Custom exponential backoff wait strategy for retrying operations.

    Args:
        retry_state: The current tenacity retry state, containing metadata about the retry attempt.

    Returns:
        float: Number of seconds to wait before the next retry attempt. The wait time uses
            exponential backoff with jitter, doubling on each failed attempt up to a maximum,
            and randomization to prevent thundering herd issues.
    """
    attempt = retry_state.attempt_number - 1

    initial_delay = 1
    max_delay = 10

    delay = min(initial_delay * (2**attempt), max_delay)

    delay *= 0.5 + random.random()

    return delay


def build_retry(
    *,
    exception_types,
    attempts: int = 3,
    wait_strategy=custom_wait,
):
    # INSERT_YOUR_CODE
    """
    Create and configure a tenacity retry decorator with the specified exception types
    and retry parameters.

    Args:
        exception_types (tuple or Exception): Exception types that should trigger a retry.
        attempts (int, optional): Maximum number of retry attempts. Defaults to 3.
        wait_strategy (callable, optional): Wait strategy for delays between retries.
            Defaults to custom exponential backoff with jitter.

    Returns:
        callable: A tenacity.retry decorator configured with the given parameters.
    """

    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_strategy,
        retry=retry_if_exception_type(exception_types),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


class RetryFactory:
    """
    Provides convenient retry decorators for service and repository methods,
    configuring standard retry policies for different layers of the application.

    Methods:
        service(): Returns a retry decorator for service-layer methods, retrying
            on network-related exceptions such as requests.exceptions.RequestException.
        repository(): Returns a retry decorator for repository/database-layer methods,
            retrying on OperationalError (SQL database errors).
    """

    @staticmethod
    def service():
        """
        Return a tenacity retry decorator for service layer methods.

        Retries the decorated function when a requests.exceptions.RequestException is raised,
        using default retry attempts and a custom wait strategy.

        Returns:
            function: A tenacity retry decorator.
        """
        return build_retry(
            exception_types=(
                requests.exceptions.RequestException,
                smtplib.SMTPException,
                TimeoutError,
            )
        )

    @staticmethod
    def repository():
        """
        Return a tenacity retry decorator for repository/database layer methods.

        Retries the decorated function when an OperationalError is raised, using default
        retry attempts and a custom wait strategy.

        Returns:
            function: A tenacity retry decorator.
        """
        return build_retry(exception_types=OperationalError)
