import abc
from typing import Optional

from internal.domains.entities import CreateUserPayload, UpdateUserPayload, UserEntity
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class AbstractUserUC(abc.ABC):
    @abc.abstractmethod
    async def create(
        self, payload: CreateUserPayload, uow: RelationalDBUnitOfWork
    ) -> Optional[UserEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: str, uow: RelationalDBUnitOfWork
    ) -> Optional[UserEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, payload: UpdateUserPayload, uow: RelationalDBUnitOfWork):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id_: str, uow: RelationalDBUnitOfWork):
        raise NotImplementedError
