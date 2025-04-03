from typing import List, Optional, Tuple

from loguru import logger

from internal.domains.entities import (
    CommentEntity,
    CreateCommentPayload,
    DeleteCommentPayload,
    GetMultiCommentsFilter,
    UpdateCommentPayload,
)
from internal.domains.errors import (
    CreateCommentException,
    DeleteCommentException,
    GetCommentException,
    GetUserException,
    UpdateCommentException,
)
from internal.domains.services.abstraction.comment import AbstractCommentSVC
from internal.domains.usecases.abstraction import AbstractCommentUC, AbstractUserUC
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class CommentSVC(AbstractCommentSVC):
    def __init__(
        self,
        relational_db_uow: RelationalDBUnitOfWork,
        comment_uc: AbstractCommentUC,
        user_uc: AbstractUserUC,
    ):
        self._relational_db_uow = relational_db_uow
        self._comment_uc = comment_uc
        self._user_uc = user_uc

    async def create(
        self, payload: CreateCommentPayload
    ) -> Tuple[Optional[CommentEntity], Optional[Exception]]:
        new_comment: Optional[CommentEntity] = None
        error: Optional[Exception] = None

        if not payload.owner_id or payload.owner_id == "":
            return None, CreateCommentException("Missing owner id")

        # start transaction
        async with self._relational_db_uow as session:
            try:
                exited_user = await self._user_uc.get_by_id(
                    id_=payload.owner_id, uow=session
                )
                if not exited_user:
                    return None, CreateCommentException(
                        f"Not found user: {payload.owner_id}"
                    )
            except GetUserException as exc:
                logger.error(exc)
                error = exc
                return None, error

            try:
                new_comment = await self._comment_uc.create(
                    payload=payload, uow=session
                )
            except CreateCommentException as exc:
                logger.error(exc)
                error = exc
                return None, error

        return new_comment, None

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

        if not payload.owner_id or payload.owner_id == "":
            return UpdateCommentException("Missing owner id")

        # start transaction
        async with self._relational_db_uow as session:
            try:
                exited_user = await self._user_uc.get_by_id(
                    id_=payload.owner_id, uow=session
                )
                if not exited_user:
                    return UpdateCommentException(f"Not found user: {payload.owner_id}")
            except GetUserException as exc:
                logger.error(exc)
                error = exc
                return error

            try:
                await self._comment_uc.update(payload=payload, uow=session)
            except UpdateCommentException as exc:
                logger.error(exc)
                error = exc
                return error

        return None

    async def delete(self, payload: DeleteCommentPayload) -> Optional[Exception]:
        error: Optional[Exception] = None

        if not payload.owner_id or payload.owner_id == "":
            return DeleteCommentException("Missing owner id")

        # start transaction
        async with self._relational_db_uow as session:
            try:
                exited_user = await self._user_uc.get_by_id(
                    id_=payload.owner_id, uow=session
                )
                if not exited_user:
                    return DeleteCommentException(f"Not found user: {payload.owner_id}")
            except GetUserException as exc:
                logger.error(exc)
                error = exc
                return error

            try:
                await self._comment_uc.delete(payload=payload, uow=session)
            except DeleteCommentException as exc:
                logger.error(exc)
                error = exc
                return error

        return None
