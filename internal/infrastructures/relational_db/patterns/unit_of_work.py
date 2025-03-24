import abc
from abc import abstractmethod
from typing import Any, Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from internal.infrastructures.relational_db import CommentRepo, PostRepo
from internal.infrastructures.relational_db.abstraction import (
    AbstractCommentRepo,
    AbstractPostRepo,
)


class AbstractUnitOfWork(abc.ABC):
    """Abstract Unit of Work for handling database transactions."""

    post_repo: AbstractPostRepo
    comment_repo: AbstractCommentRepo

    def __init__(
        self,
        post_repo: AbstractPostRepo,
        comment_repo: AbstractCommentRepo,
    ):
        self.post_repo = post_repo
        self.comment_repo = comment_repo

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
        session: AsyncSession,
        scoped_session: async_scoped_session[AsyncSession],
        post_repo: PostRepo,
        comment_repo: CommentRepo,
    ):
        super().__init__(
            post_repo=post_repo,
            comment_repo=comment_repo,
        )
        self._session = session
        self._scoped_session = scoped_session

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Any,
    ):
        try:
            if exc_type is None:
                await self._session.commit()
            else:
                await self._session.rollback()
        finally:
            await self._session.close()
            await self.remove()

    async def remove(self):
        """Removes the scoped session from SQLAlchemy async session."""

        await self._scoped_session.remove()
