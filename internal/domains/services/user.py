from typing import List, Optional, Tuple

from loguru import logger

from internal.domains.entities import (
    CommentEntity,
    CreateUserPayload,
    DeleteCommentPayload,
    DeletePostPayload,
    GetMultiCommentsFilter,
    GetMultiPostsFilter,
    PostEntity,
    UpdateUserPayload,
    UserEntity,
)
from internal.domains.errors import (
    CreateUserException,
    DeleteCommentException,
    DeletePostException,
    DeleteUserException,
    GetCommentException,
    GetPostException,
    GetUserException,
    UpdateUserException,
)
from internal.domains.services.abstraction import AbstractUserSVC
from internal.domains.usecases.abstraction import (
    AbstractCommentUC,
    AbstractPostUC,
    AbstractUserUC,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class UserSVC(AbstractUserSVC):
    def __init__(
        self,
        relational_db_uow: RelationalDBUnitOfWork,
        user_uc: AbstractUserUC,
        post_uc: AbstractPostUC,
        comment_uc: AbstractCommentUC,
    ):
        self._relational_db_uow = relational_db_uow
        self._user_uc = user_uc
        self._post_uc = post_uc
        self._comment_uc = comment_uc

    async def create(
        self, payload: CreateUserPayload
    ) -> Tuple[Optional[UserEntity], Optional[Exception]]:
        new_user: Optional[UserEntity] = None
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                new_user = await self._user_uc.create(payload=payload, uow=session)
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
            # start transaction
            async with self._relational_db_uow as session:
                await self._user_uc.update(payload=payload, uow=session)
        except UpdateUserException as exc:
            logger.error(exc)
            error = exc

        return error

    async def delete(self, id_: str) -> Optional[Exception]:
        error: Optional[Exception] = None

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
                logger.error(exc)
                error = exc
                return error

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
                    logger.error(exc)
                    error = exc
                    return error

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
                logger.error(exc)
                error = exc
                return error

            # delete one by one post
            for post in posts:
                try:
                    delete_post_payload = DeletePostPayload(
                        id_=str(post.id_),
                        owner_id=id_,
                    )
                    await self._post_uc.delete(payload=delete_post_payload, uow=session)
                except DeletePostException as exc:
                    logger.error(exc)
                    error = exc
                    return error

            # delete this user
            try:
                await self._user_uc.delete(id_=id_, uow=session)
            except DeleteUserException as exc:
                logger.error(exc)
                error = exc
                return error

        return error
