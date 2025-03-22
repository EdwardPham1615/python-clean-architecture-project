import abc
from typing import Optional, Tuple, List

from internal.domains.entities import (
    CreatePostPayload,
    PostEntity,
    GetMultiPostsFilter,
    UpdatePostPayload,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)
from internal.infrastructures.relational_db.abstraction import (
    AbstractPostRepo as RelationalDBAbstractPostRepo,
)


class AbstractPostUC(abc.ABC):
    relational_db_post_repo: RelationalDBAbstractPostRepo

    @abc.abstractmethod
    async def create(
        self, payload: CreatePostPayload, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Optional[PostEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: str, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Optional[PostEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_multi(
        self, filter_: GetMultiPostsFilter, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Tuple[List[PostEntity], Optional[int]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(
        self, payload: UpdatePostPayload, uow: Optional[RelationalDBUnitOfWork] = None
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id_: str, uow: Optional[RelationalDBUnitOfWork] = None):
        raise NotImplementedError
