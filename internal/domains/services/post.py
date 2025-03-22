from typing import Optional, Tuple, List

from loguru import logger

from internal.domains.entities import (
    CreatePostPayload,
    PostEntity,
    GetMultiPostsFilter,
    UpdatePostPayload,
    GetMultiCommentsFilter,
    CommentEntity,
)
from internal.domains.errors import (
    CreatePostException,
    GetPostException,
    UpdatePostException,
    DeletePostException,
    GetCommentException,
    DeleteCommentException,
)
from internal.domains.services.abstraction import AbstractPostSVC
from internal.domains.usecases.abstraction import AbstractPostUC, AbstractCommentUC
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class PostSVC(AbstractPostSVC):
    def __init__(
        self,
        relational_db_uow: RelationalDBUnitOfWork,
        post_uc: AbstractPostUC,
        comment_uc: AbstractCommentUC,
    ):
        self._relational_db_uow = relational_db_uow
        self._post_uc = post_uc
        self._comment_uc = comment_uc

    async def create(
        self, payload: CreatePostPayload
    ) -> Tuple[Optional[PostEntity], Optional[Exception]]:
        new_post: Optional[PostEntity] = None
        error: Optional[Exception] = None

        try:
            # start transaction
            async with self._relational_db_uow as session:
                new_post = await self._post_uc.create(payload=payload, uow=session)
        except CreatePostException as exc:
            logger.error(exc)
            error = exc

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

        try:
            # start transaction
            async with self._relational_db_uow as session:
                await self._post_uc.update(payload=payload, uow=session)
        except UpdatePostException as exc:
            logger.error(exc)
            error = exc

        return error

    async def delete(self, id_: str) -> Optional[Exception]:
        error: Optional[Exception] = None

        # start transaction
        async with self._relational_db_uow as session:
            # get all comments of this post
            try:
                comments: List[CommentEntity] = []
                (comments, _) = await self._comment_uc.get_multi(
                    filter_=GetMultiCommentsFilter(
                        enable_count=False,
                        post_id=id_,
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
                    await self._comment_uc.delete(id_=str(comment.id_), uow=session)
                except DeleteCommentException as exc:
                    logger.error(exc)
                    error = exc
                    return error

            # delete this post
            try:
                await self._post_uc.delete(id_=id_, uow=session)
            except DeletePostException as exc:
                logger.error(exc)
                error = exc
                return error

        return error
