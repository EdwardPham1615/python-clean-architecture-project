from typing import List, Optional, Tuple

from internal.domains.constants import V1ReBACObjectType, V1ReBACRelation
from internal.domains.entities import (
    CommentEntity,
    CreateUserPayload,
    DeleteCommentPayload,
    DeletePostPayload,
    GetMultiCommentsFilter,
    GetMultiPostsFilter,
    PermEntity,
    PostEntity,
    UpdateUserPayload,
    UserEntity,
)
from internal.domains.errors import (
    CheckPermException,
    CreatePermException,
    CreateUserException,
    DeleteCommentException,
    DeletePostException,
    DeleteUserException,
    GetCommentException,
    GetPostException,
    GetUserException,
    UnauthorizeException,
    UpdateUserException,
)
from internal.domains.services.abstraction import AbstractUserSVC
from internal.domains.usecases.abstraction import (
    AbstractAuthorizationUC,
    AbstractCommentUC,
    AbstractPostUC,
    AbstractUserUC,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)
from utils.logger_utils import get_shared_logger

logger = get_shared_logger()


class UserSVC(AbstractUserSVC):
    def __init__(
        self,
        relational_db_uow: RelationalDBUnitOfWork,
        user_uc: AbstractUserUC,
        post_uc: AbstractPostUC,
        comment_uc: AbstractCommentUC,
        authorization_uc: AbstractAuthorizationUC,
    ):
        self._relational_db_uow = relational_db_uow
        self._user_uc = user_uc
        self._post_uc = post_uc
        self._comment_uc = comment_uc
        self._authorization_uc = authorization_uc

    async def create(
        self, payload: CreateUserPayload
    ) -> Tuple[Optional[UserEntity], Optional[Exception]]:
        new_user: Optional[UserEntity] = None
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                new_user = await self._user_uc.create(payload=payload, uow=session)

                # set owner permission
                try:
                    await self._authorization_uc.create_perms(
                        entities=[
                            PermEntity(
                                target_obj=f"{V1ReBACObjectType.USER.value}:{str(new_user.id_)}",
                                relation=f"{V1ReBACRelation.IS_OWNER.value}",
                                request_obj=f"{V1ReBACObjectType.USER.value}:{str(new_user.id_)}",
                            )
                        ]
                    )
                except CreatePermException as exc:
                    raise CreateUserException(exc)

        except CreateUserException as exc:
            logger.error(exc)
            error = exc

        return new_user, error

    async def get_by_id(
        self, id_: str
    ) -> Tuple[Optional[UserEntity], Optional[Exception]]:
        user: Optional[UserEntity] = None
        error: Optional[Exception] = None

        try:
            try:
                is_allowed = await self._authorization_uc.check_single_perm(
                    entity=PermEntity(
                        target_obj=f"{V1ReBACObjectType.USER.value}:{id_}",
                        relation=f"{V1ReBACRelation.CAN_GET_DETAIL.value}",
                        request_obj=f"{V1ReBACObjectType.USER.value}:{id_}",
                    )
                )
                if not is_allowed:
                    return None, UnauthorizeException("Unauthorized")
            except CheckPermException as exc:
                raise GetUserException(exc)

            # start transaction
            async with self._relational_db_uow as session:
                user = await self._user_uc.get_by_id(id_=id_, uow=session)
        except GetUserException as exc:
            logger.error(exc)
            error = exc

        return user, error

    async def update(self, payload: UpdateUserPayload) -> Optional[Exception]:
        error: Optional[Exception] = None

        try:
            try:
                is_allowed = await self._authorization_uc.check_single_perm(
                    entity=PermEntity(
                        target_obj=f"{V1ReBACObjectType.USER.value}:{payload.id_}",
                        relation=f"{V1ReBACRelation.CAN_UPDATE.value}",
                        request_obj=f"{V1ReBACObjectType.USER.value}:{payload.id_}",
                    )
                )
                if not is_allowed:
                    return UnauthorizeException("Unauthorized")
            except CheckPermException as exc:
                raise UpdateUserException(exc)

            # start transaction
            async with self._relational_db_uow as session:
                await self._user_uc.update(payload=payload, uow=session)
        except UpdateUserException as exc:
            logger.error(exc)
            error = exc

        return error

    async def delete(self, id_: str) -> Optional[Exception]:
        error: Optional[Exception] = None
        try:
            try:
                is_allowed = await self._authorization_uc.check_single_perm(
                    entity=PermEntity(
                        target_obj=f"{V1ReBACObjectType.USER.value}:{id_}",
                        relation=f"{V1ReBACRelation.CAN_UPDATE.value}",
                        request_obj=f"{V1ReBACObjectType.USER.value}:{id_}",
                    )
                )
                if not is_allowed:
                    return UnauthorizeException("Unauthorized")
            except CheckPermException as exc:
                raise DeleteUserException(exc)

            # start transaction
            async with self._relational_db_uow as session:
                # get all comments of this user
                try:
                    comments: List[CommentEntity] = []
                    (comments, _) = await self._comment_uc.get_multi(
                        filter_=GetMultiCommentsFilter(
                            enable_count=False,
                            owner_id=id_,
                        ),
                        uow=session,
                    )
                except GetCommentException as exc:
                    raise DeleteUserException(exc)

                # delete one by one comment
                for comment in comments:
                    try:
                        delete_comment_payload = DeleteCommentPayload(
                            id_=str(comment.id_),
                            owner_id=id_,
                        )
                        await self._comment_uc.delete(
                            payload=delete_comment_payload, uow=session
                        )
                    except DeleteCommentException as exc:
                        raise DeleteUserException(exc)

                # get all posts of this user
                try:
                    posts: List[PostEntity] = []
                    (posts, _) = await self._post_uc.get_multi(
                        filter_=GetMultiPostsFilter(
                            enable_count=False,
                            owner_id=id_,
                        ),
                        uow=session,
                    )
                except GetPostException as exc:
                    raise DeleteUserException(exc)

                # delete one by one post
                for post in posts:
                    try:
                        delete_post_payload = DeletePostPayload(
                            id_=str(post.id_),
                            owner_id=id_,
                        )
                        await self._post_uc.delete(
                            payload=delete_post_payload, uow=session
                        )
                    except DeletePostException as exc:
                        raise DeleteUserException(exc)

                # delete this user
                await self._user_uc.delete(id_=id_, uow=session)

        except DeleteUserException as exc:
            logger.error(exc)
            error = exc

        return error
