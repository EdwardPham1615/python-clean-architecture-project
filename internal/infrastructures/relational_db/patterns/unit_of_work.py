import abc
import logging
from abc import abstractmethod
from typing import Callable, Optional

from asyncpg.exceptions import SerializationError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncSessionTransaction,
    async_scoped_session,
)
from tenacity import (
    RetryError,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from internal.infrastructures.relational_db import CommentRepo, PostRepo, UserRepo
from internal.infrastructures.relational_db.abstraction import (
    AbstractCommentRepo,
    AbstractPostRepo,
    AbstractUserRepo,
)
from utils.logger_utils import get_shared_logger


class AbstractUnitOfWork(abc.ABC):
    """Abstract Unit of Work for handling database transactions."""

    post_repo: AbstractPostRepo
    comment_repo: AbstractCommentRepo
    user_repo: AbstractUserRepo

    def __init__(
        self,
        post_repo: AbstractPostRepo,
        comment_repo: AbstractCommentRepo,
        user_repo: AbstractUserRepo,
    ):
        self.post_repo = post_repo
        self.comment_repo = comment_repo
        self.user_repo = user_repo

    @abstractmethod
    async def __aenter__(self) -> "AbstractUnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError


class AsyncSQLAlchemyUnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy-based Unit of Work for async operations."""

    def __init__(
        self,
        scoped_session: async_scoped_session[AsyncSession],
        post_repo_factory: Callable[[AsyncSession], PostRepo],
        comment_repo_factory: Callable[[AsyncSession], CommentRepo],
        user_repo_factory: Callable[[AsyncSession], UserRepo],
    ):
        self._scoped_session_factory = scoped_session
        self._session: Optional[AsyncSession] = None
        self._transaction: Optional[AsyncSessionTransaction] = None
        self._post_repo_factory = post_repo_factory
        self._comment_repo_factory = comment_repo_factory
        self._user_repo_factory = user_repo_factory

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        retry=retry_if_exception_type(SerializationError),
        before_sleep=before_sleep_log(get_shared_logger(), logging.WARNING),
    )
    async def _init_session(self):
        """Initialize session with retry logic for serialization errors."""
        self._session = self._scoped_session_factory()
        self._transaction = await self._session.begin()

        # register repos
        self.post_repo = self._post_repo_factory(self._session)
        self.comment_repo = self._comment_repo_factory(self._session)
        self.user_repo = self._user_repo_factory(self._session)
        return self

    async def __aenter__(self):
        try:
            return await self._init_session()
        except SerializationError as e:
            # Ensure resources are cleaned up if all retries fail
            if self._session:
                await self._session.close()
                await self._scoped_session_factory.remove()
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        retry=retry_if_exception_type(SerializationError),
        before_sleep=before_sleep_log(get_shared_logger(), logging.WARNING),
    )
    async def _commit_transaction(self):
        """Commit transaction with retry logic for serialization errors."""
        try:
            await self._transaction.commit()
        except SerializationError:
            # Rollback the failed transaction and start a new one for retry
            await self._transaction.rollback()
            self._transaction = await self._session.begin()
            # Re-raise to trigger retry
            raise

    async def __aexit__(self, exc_type, exc, tb):
        logger = get_shared_logger()

        try:
            if exc_type is None:
                try:
                    # Try to commit with retries
                    await self._commit_transaction()
                except RetryError as e:
                    # All retries exhausted
                    logger.error(f"Max retries exceeded for commit: {e}")
                    await self._transaction.rollback()
                    raise SerializationError(
                        "Failed to commit transaction after multiple retries"
                    ) from e
            else:
                # If there was an exception in the context, just rollback
                await self._transaction.rollback()
        finally:
            await self._session.close()
            await self._scoped_session_factory.remove()
