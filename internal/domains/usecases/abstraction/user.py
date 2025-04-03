import abc
from typing import Optional

from internal.domains.entities import CreateUserPayload, UpdateUserPayload, UserEntity
from internal.infrastructures.relational_db.abstraction import (
    AbstractUserRepo as RelationalDBAbstractUserRepo,
)
from internal.infrastructures.relational_db.patterns import AbstractUnitOfWork
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class AbstractUserUC(abc.ABC):
    relational_db_user_repo: RelationalDBAbstractUserRepo

    @abc.abstractmethod
    async def create(
        self, payload: CreateUserPayload, uow: Optional[AbstractUnitOfWork] = None
    ) -> Optional[UserEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: str, uow: Optional[AbstractUnitOfWork] = None
    ) -> Optional[UserEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(
        self, payload: UpdateUserPayload, uow: Optional[RelationalDBUnitOfWork] = None
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id_: str, uow: Optional[RelationalDBUnitOfWork] = None):
        raise NotImplementedError
