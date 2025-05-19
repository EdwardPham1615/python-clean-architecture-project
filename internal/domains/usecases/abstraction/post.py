import abc
from typing import List, Optional, Tuple

from internal.domains.entities import (
    CreatePostPayload,
    DeletePostPayload,
    GetMultiPostsFilter,
    PostEntity,
    UpdatePostPayload,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class AbstractPostUC(abc.ABC):
    @abc.abstractmethod
    async def create(
        self, payload: CreatePostPayload, uow: RelationalDBUnitOfWork
    ) -> Optional[PostEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: str, uow: RelationalDBUnitOfWork
    ) -> Optional[PostEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_multi(
        self, filter_: GetMultiPostsFilter, uow: RelationalDBUnitOfWork
    ) -> Tuple[List[PostEntity], Optional[int]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, payload: UpdatePostPayload, uow: RelationalDBUnitOfWork):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, payload: DeletePostPayload, uow: RelationalDBUnitOfWork):
        raise NotImplementedError
