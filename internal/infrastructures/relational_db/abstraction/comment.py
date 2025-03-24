import abc
from typing import List, Optional, Tuple

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from internal.domains.entities import CommentEntity, GetMultiCommentsFilter


class AbstractCommentRepo(abc.ABC):
    session: AsyncSession

    @abc.abstractmethod
    async def create(
        self, entity: CommentEntity, uow_session: Optional[AsyncSession] = None
    ) -> UUID4:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: UUID4, uow_session: Optional[AsyncSession] = None
    ) -> Optional[CommentEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_multi(
        self,
        filter_: GetMultiCommentsFilter,
        uow_session: Optional[AsyncSession] = None,
    ) -> Tuple[List[CommentEntity], Optional[int]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(
        self, entity: CommentEntity, uow_session: Optional[AsyncSession] = None
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id_: UUID4, uow_session: Optional[AsyncSession] = None):
        raise NotImplementedError
