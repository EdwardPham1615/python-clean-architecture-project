import abc
from typing import Optional, Tuple, List

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from internal.domains.entities import PostEntity, GetMultiPostsFilter


class AbstractPostRepo(abc.ABC):
    session: AsyncSession

    @abc.abstractmethod
    async def create(
        self, entity: PostEntity, uow_session: Optional[AsyncSession] = None
    ) -> UUID4:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: UUID4, uow_session: Optional[AsyncSession] = None
    ) -> Optional[PostEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_multi(
        self, filter_: GetMultiPostsFilter, uow_session: Optional[AsyncSession] = None
    ) -> Tuple[List[PostEntity], Optional[int]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(
        self, entity: PostEntity, uow_session: Optional[AsyncSession] = None
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id_: UUID4, uow_session: Optional[AsyncSession] = None):
        raise NotImplementedError
