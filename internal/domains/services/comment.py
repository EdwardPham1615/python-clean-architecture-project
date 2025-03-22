from typing import Optional, Tuple, List

from loguru import logger

from internal.domains.entities import (
    CreateCommentPayload,
    CommentEntity,
    GetMultiCommentsFilter,
    UpdateCommentPayload,
)
from internal.domains.errors import (
    CreateCommentException,
    GetCommentException,
    UpdateCommentException,
    DeleteCommentException,
)
from internal.domains.services.abstraction.comment import AbstractCommentSVC
from internal.domains.usecases.abstraction import AbstractCommentUC
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class CommentSVC(AbstractCommentSVC):
    def __init__(
        self, relational_db_uow: RelationalDBUnitOfWork, comment_uc: AbstractCommentUC
    ):
        self._relational_db_uow = relational_db_uow
        self._comment_uc = comment_uc

    async def create(
        self, payload: CreateCommentPayload
    ) -> Tuple[Optional[CommentEntity], Optional[Exception]]:
        new_comment: Optional[CommentEntity] = None
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                new_comment = await self._comment_uc.create(
                    payload=payload, uow=session
                )
        except CreateCommentException as exc:
            logger.error(exc)
            error = exc

        return new_comment, error

    async def get_by_id(
        self, id_: str
    ) -> Tuple[Optional[CommentEntity], Optional[Exception]]:
        comment: Optional[CommentEntity] = None
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                comment = await self._comment_uc.get_by_id(id_=id_, uow=session)
        except GetCommentException as exc:
            logger.error(exc)
            error = exc

        return comment, error

    async def get_multi(
        self, filter_: GetMultiCommentsFilter
    ) -> Tuple[Tuple[List[CommentEntity], Optional[int]], Optional[Exception]]:
        res: Tuple[List[CommentEntity], Optional[int]] = ([], None)
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                res = await self._comment_uc.get_multi(filter_=filter_, uow=session)
        except GetCommentException as exc:
            logger.error(exc)
            error = exc

        return res, error

    async def update(self, payload: UpdateCommentPayload) -> Optional[Exception]:
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                await self._comment_uc.update(payload=payload, uow=session)
        except UpdateCommentException as exc:
            logger.error(exc)
            error = exc

        return error

    async def delete(self, id_: str) -> Optional[Exception]:
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                await self._comment_uc.delete(id_=id_, uow=session)
        except DeleteCommentException as exc:
            logger.error(exc)
            error = exc

        return error
