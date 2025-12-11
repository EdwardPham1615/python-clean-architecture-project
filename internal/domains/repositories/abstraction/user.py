import abc
from typing import Optional

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from internal.domains.entities import UserEntity


class AbstractUserRepo(abc.ABC):
    session: AsyncSession

    @abc.abstractmethod
    async def create(self, entity: UserEntity) -> UUID4:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(self, id_: UUID4) -> Optional[UserEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, entity: UserEntity):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id_: UUID4):
        raise NotImplementedError
