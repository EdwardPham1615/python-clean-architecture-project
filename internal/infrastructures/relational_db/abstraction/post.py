import abc
from typing import List, Optional, Tuple

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from internal.domains.entities import GetMultiPostsFilter, PostEntity


class AbstractPostRepo(abc.ABC):
    session: AsyncSession

    @abc.abstractmethod
    async def create(self, entity: PostEntity) -> UUID4:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, id_: UUID4) -> Optional[PostEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_multi(
        self, filter_: GetMultiPostsFilter
    ) -> Tuple[List[PostEntity], Optional[int]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, entity: PostEntity):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id_: UUID4):
        raise NotImplementedError
