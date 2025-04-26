from typing import List, Optional, Tuple

from internal.domains.constants import V1ReBACObjectType, V1ReBACRelation
from internal.domains.entities import (
    CommentEntity,
    CreateCommentPayload,
    DeleteCommentPayload,
    GetMultiCommentsFilter,
    PermEntity,
    UpdateCommentPayload,
)
from internal.domains.errors import (
    CheckPermException,
    CreateCommentException,
    CreatePermException,
    DeleteCommentException,
    GetCommentException,
    GetUserException,
    UnauthorizeException,
    UpdateCommentException,
)
from internal.domains.services.abstraction.comment import AbstractCommentSVC
from internal.domains.usecases.abstraction import (
    AbstractAuthorizationUC,
    AbstractCommentUC,
    AbstractUserUC,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)
from utils.logger_utils import get_shared_logger

logger = get_shared_logger()


class CommentSVC(AbstractCommentSVC):
    def __init__(
        self,
        relational_db_uow: RelationalDBUnitOfWork,
        comment_uc: AbstractCommentUC,
        user_uc: AbstractUserUC,
        authorization_uc: AbstractAuthorizationUC,
    ):
        self._relational_db_uow = relational_db_uow
        self._comment_uc = comment_uc
        self._user_uc = user_uc
        self._authorization_uc = authorization_uc

    async def create(
        self, payload: CreateCommentPayload
    ) -> Tuple[Optional[CommentEntity], Optional[Exception]]:
        new_comment: Optional[CommentEntity] = None
        error: Optional[Exception] = None

        if not payload.owner_id or payload.owner_id == "":
            return None, CreateCommentException("Missing owner id")

        try:
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
                    raise CreateCommentException(exc)

                new_comment = await self._comment_uc.create(
                    payload=payload, uow=session
                )

                # set owner permission
                try:
                    await self._authorization_uc.create_perms(
                        entities=[
                            PermEntity(
                                target_obj=f"{V1ReBACObjectType.USER.value}:{payload.owner_id}",
                                relation=f"{V1ReBACRelation.IS_OWNER.value}",
                                request_obj=f"{V1ReBACObjectType.COMMENT.value}:{str(new_comment.id_)}",
                            )
                        ]
                    )
                except CreatePermException as exc:
                    raise CreateCommentException(exc)

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

        if not payload.owner_id or payload.owner_id == "":
            return UpdateCommentException("Missing owner id")

        try:
            try:
                is_allowed = await self._authorization_uc.check_single_perm(
                    entity=PermEntity(
                        target_obj=f"{V1ReBACObjectType.USER.value}:{payload.owner_id}",
                        relation=f"{V1ReBACRelation.CAN_UPDATE.value}",
                        request_obj=f"{V1ReBACObjectType.COMMENT.value}:{payload.id_}",
                    )
                )
                if not is_allowed:
                    return UnauthorizeException("Unauthorized")
            except CheckPermException as exc:
                raise UpdateCommentException(exc)

            # start transaction
            async with self._relational_db_uow as session:
                try:
                    exited_user = await self._user_uc.get_by_id(
                        id_=payload.owner_id, uow=session
                    )
                    if not exited_user:
                        return UpdateCommentException(
                            f"Not found user: {payload.owner_id}"
                        )
                except GetUserException as exc:
                    raise UpdateCommentException(exc)

                await self._comment_uc.update(payload=payload, uow=session)

        except UpdateCommentException as exc:
            logger.error(exc)
            error = exc

        return error

    async def delete(self, payload: DeleteCommentPayload) -> Optional[Exception]:
        error: Optional[Exception] = None

        if not payload.owner_id or payload.owner_id == "":
            return DeleteCommentException("Missing owner id")

        try:
            try:
                is_allowed = await self._authorization_uc.check_single_perm(
                    entity=PermEntity(
                        target_obj=f"{V1ReBACObjectType.USER.value}:{payload.owner_id}",
                        relation=f"{V1ReBACRelation.CAN_DELETE.value}",
                        request_obj=f"{V1ReBACObjectType.COMMENT.value}:{payload.id_}",
                    )
                )
                if not is_allowed:
                    return UnauthorizeException("Unauthorized")
            except CheckPermException as exc:
                raise DeleteCommentException(exc)

            # start transaction
            async with self._relational_db_uow as session:
                try:
                    exited_user = await self._user_uc.get_by_id(
                        id_=payload.owner_id, uow=session
                    )
                    if not exited_user:
                        return DeleteCommentException(
                            f"Not found user: {payload.owner_id}"
                        )
                except GetUserException as exc:
                    raise DeleteCommentException(exc)

                await self._comment_uc.delete(payload=payload, uow=session)

        except DeleteCommentException as exc:
            logger.error(exc)
            error = exc

        return error
