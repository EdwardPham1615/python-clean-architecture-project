from typing import List, Optional, Tuple

from loguru import logger

from internal.domains.constants import V1ReBACObjectType, V1ReBACRelation
from internal.domains.entities import (
    CommentEntity,
    CreatePostPayload,
    DeleteCommentPayload,
    DeletePostPayload,
    GetMultiCommentsFilter,
    GetMultiPostsFilter,
    PermEntity,
    PostEntity,
    UpdatePostPayload,
)
from internal.domains.errors import (
    CheckPermException,
    CreatePermException,
    CreatePostException,
    DeleteCommentException,
    DeletePostException,
    GetCommentException,
    GetPostException,
    GetUserException,
    UnauthorizeException,
    UpdatePostException,
)
from internal.domains.services.abstraction import AbstractPostSVC
from internal.domains.usecases.abstraction import (
    AbstractAuthorizationUC,
    AbstractCommentUC,
    AbstractPostUC,
    AbstractUserUC,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class PostSVC(AbstractPostSVC):
    def __init__(
        self,
        relational_db_uow: RelationalDBUnitOfWork,
        post_uc: AbstractPostUC,
        comment_uc: AbstractCommentUC,
        user_uc: AbstractUserUC,
        authorization_uc: AbstractAuthorizationUC,
    ):
        self._relational_db_uow = relational_db_uow
        self._post_uc = post_uc
        self._comment_uc = comment_uc
        self._user_uc = user_uc
        self._authorization_uc = authorization_uc

    async def create(
        self, payload: CreatePostPayload
    ) -> Tuple[Optional[PostEntity], Optional[Exception]]:
        new_post: Optional[PostEntity] = None
        error: Optional[Exception] = None

        if not payload.owner_id or payload.owner_id == "":
            return None, CreatePostException("Missing owner id")

        try:
            # start transaction
            async with self._relational_db_uow as session:
                try:
                    exited_user = await self._user_uc.get_by_id(
                        id_=payload.owner_id, uow=session
                    )
                    if not exited_user:
                        return None, CreatePostException(
                            f"Not found user: {payload.owner_id}"
                        )
                except GetUserException as exc:
                    raise CreatePostException(exc)

                new_post = await self._post_uc.create(payload=payload, uow=session)

                # set owner permission
                try:
                    await self._authorization_uc.create_perms(
                        entities=[
                            PermEntity(
                                target_obj=f"{V1ReBACObjectType.USER.value}:{payload.owner_id}",
                                relation=f"{V1ReBACRelation.IS_OWNER.value}",
                                request_obj=f"{V1ReBACObjectType.POST.value}:{str(new_post.id_)}",
                            )
                        ]
                    )
                except CreatePermException as exc:
                    raise CreatePostException(exc)

        except CreatePostException as exc:
            logger.error(exc)
            error = exc
            return None, error

        return new_post, error

    async def get_by_id(
        self, id_: str
    ) -> Tuple[Optional[PostEntity], Optional[Exception]]:
        post: Optional[PostEntity] = None
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                post = await self._post_uc.get_by_id(id_=id_, uow=session)
        except GetPostException as exc:
            logger.error(exc)
            error = exc

        return post, error

    async def get_multi(
        self, filter_: GetMultiPostsFilter
    ) -> Tuple[Tuple[List[PostEntity], Optional[int]], Optional[Exception]]:
        res: Tuple[List[PostEntity], Optional[int]] = ([], None)
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                res = await self._post_uc.get_multi(filter_=filter_, uow=session)
        except GetPostException as exc:
            logger.error(exc)
            error = exc

        return res, error

    async def update(self, payload: UpdatePostPayload) -> Optional[Exception]:
        error: Optional[Exception] = None

        if not payload.owner_id or payload.owner_id == "":
            return UpdatePostException("Missing owner id")

        try:
            try:
                is_allowed = await self._authorization_uc.check_single_perm(
                    entity=PermEntity(
                        target_obj=f"{V1ReBACObjectType.USER.value}:{payload.owner_id}",
                        relation=f"{V1ReBACRelation.CAN_UPDATE.value}",
                        request_obj=f"{V1ReBACObjectType.POST.value}:{payload.id_}",
                    )
                )
                if not is_allowed:
                    return UnauthorizeException("Unauthorized")
            except CheckPermException as exc:
                raise UpdatePostException(exc)

            # start transaction
            async with self._relational_db_uow as session:
                try:
                    exited_user = await self._user_uc.get_by_id(
                        id_=payload.owner_id, uow=session
                    )
                    if not exited_user:
                        return UpdatePostException(
                            f"Not found user: {payload.owner_id}"
                        )
                except GetUserException as exc:
                    raise UpdatePostException(exc)

                await self._post_uc.update(payload=payload, uow=session)

        except UpdatePostException as exc:
            logger.error(exc)
            error = exc

        return error

    async def delete(self, payload: DeletePostPayload) -> Optional[Exception]:
        error: Optional[Exception] = None

        if not payload.owner_id or payload.owner_id == "":
            return DeletePostException("Missing owner id")

        try:
            try:
                is_allowed = await self._authorization_uc.check_single_perm(
                    entity=PermEntity(
                        target_obj=f"{V1ReBACObjectType.USER.value}:{payload.owner_id}",
                        relation=f"{V1ReBACRelation.CAN_DELETE.value}",
                        request_obj=f"{V1ReBACObjectType.POST.value}:{payload.id_}",
                    )
                )
                if not is_allowed:
                    return UnauthorizeException("Unauthorized")
            except CheckPermException as exc:
                raise DeletePostException(exc)

            # start transaction
            async with self._relational_db_uow as session:
                try:
                    exited_user = await self._user_uc.get_by_id(
                        id_=payload.owner_id, uow=session
                    )
                    if not exited_user:
                        return DeletePostException(
                            f"Not found user: {payload.owner_id}"
                        )
                except GetUserException as exc:
                    raise DeletePostException(exc)

                # get all comments of this post
                try:
                    comments: List[CommentEntity] = []
                    (comments, _) = await self._comment_uc.get_multi(
                        filter_=GetMultiCommentsFilter(
                            enable_count=False,
                            post_id=payload.id_,
                        ),
                        uow=session,
                    )
                except GetCommentException as exc:
                    raise DeletePostException(exc)

                # delete one by one comment
                for comment in comments:
                    try:
                        delete_comment_payload = DeleteCommentPayload(
                            id_=str(comment.id_),
                            owner_id=payload.owner_id,
                        )
                        await self._comment_uc.delete(
                            payload=delete_comment_payload, uow=session
                        )
                    except DeleteCommentException as exc:
                        raise DeletePostException(exc)

                # delete this post
                await self._post_uc.delete(payload=payload, uow=session)

        except DeletePostException as exc:
            logger.error(exc)
            error = exc

        return error
