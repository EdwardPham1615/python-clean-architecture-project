import abc
from abc import abstractmethod
from typing import Any, Callable, Optional, Type

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncSessionTransaction,
    async_scoped_session,
)

from internal.infrastructures.relational_db import CommentRepo, PostRepo, UserRepo
from internal.infrastructures.relational_db.abstraction import (
    AbstractCommentRepo,
    AbstractPostRepo,
    AbstractUserRepo,
)


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

    async def __aenter__(self):
        self._session = self._scoped_session_factory()
        self._transaction = await self._session.begin()

        # register repo
        self.post_repo = self._post_repo_factory(self._session)
        self.comment_repo = self._comment_repo_factory(self._session)
        self.user_repo = self._user_repo_factory(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Any,
    ):
        try:
            if exc_type is None:
                await self._transaction.commit()
            else:
                await self._transaction.rollback()
        except Exception:
            await self._transaction.rollback()
            raise
        finally:
            await self._session.close()
            await self._scoped_session_factory.remove()
