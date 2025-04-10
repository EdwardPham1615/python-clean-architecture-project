import abc
from typing import List, Optional, Tuple

from internal.domains.entities import (
    CommentEntity,
    CreateCommentPayload,
    DeleteCommentPayload,
    GetMultiCommentsFilter,
    UpdateCommentPayload,
)
from internal.infrastructures.relational_db.abstraction import (
    AbstractCommentRepo as RelationalDBAbstractCommentRepo,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class AbstractCommentUC(abc.ABC):
    relational_db_comment_repo: RelationalDBAbstractCommentRepo

    @abc.abstractmethod
    async def create(
        self,
        payload: CreateCommentPayload,
        uow: Optional[RelationalDBUnitOfWork] = None,
    ) -> Optional[CommentEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: str, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Optional[CommentEntity]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_multi(
        self,
        filter_: GetMultiCommentsFilter,
        uow: Optional[RelationalDBUnitOfWork] = None,
    ) -> Tuple[List[CommentEntity], Optional[int]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(
        self,
        payload: UpdateCommentPayload,
        uow: Optional[RelationalDBUnitOfWork] = None,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(
        self,
        payload: DeleteCommentPayload,
        uow: Optional[RelationalDBUnitOfWork] = None,
    ):
        raise NotImplementedError
