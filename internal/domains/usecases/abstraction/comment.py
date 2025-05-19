import abc
from typing import List, Optional, Tuple

from internal.domains.entities import (
    CommentEntity,
    CreateCommentPayload,
    DeleteCommentPayload,
    GetMultiCommentsFilter,
    UpdateCommentPayload,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class AbstractCommentUC(abc.ABC):
    @abc.abstractmethod
    async def create(
        self,
        payload: CreateCommentPayload,
        uow: RelationalDBUnitOfWork,
    ) -> Optional[CommentEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: str, uow: RelationalDBUnitOfWork
    ) -> Optional[CommentEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_multi(
        self,
        filter_: GetMultiCommentsFilter,
        uow: RelationalDBUnitOfWork,
    ) -> Tuple[List[CommentEntity], Optional[int]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(
        self,
        payload: UpdateCommentPayload,
        uow: RelationalDBUnitOfWork,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(
        self,
        payload: DeleteCommentPayload,
        uow: RelationalDBUnitOfWork,
    ):
        raise NotImplementedError
