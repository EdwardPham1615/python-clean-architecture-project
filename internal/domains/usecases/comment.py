import uuid
from datetime import UTC, datetime
from typing import List, Optional, Tuple

from pydantic import UUID4

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
    UpdateCommentException,
)
from internal.domains.usecases.abstraction import AbstractCommentUC
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)
from utils.logger_utils import get_shared_logger
from utils.time_utils import DATETIME_DEFAULT_FORMAT, from_str_to_dt

logger = get_shared_logger()


class CommentUC(AbstractCommentUC):
    def __init__(self):
        pass

    async def create(
        self,
        payload: CreateCommentPayload,
        uow: RelationalDBUnitOfWork,
    ) -> Optional[CommentEntity]:
        try:
            session = uow.comment_repo

            entity = CommentEntity(
                id_=uuid.uuid4(),
                text_content=payload.text_content,
                created_at=datetime.now(tz=UTC),
                post_id=UUID4(payload.post_id),
                owner_id=UUID4(payload.owner_id),
            )
            if payload.id_:
                entity.id_ = UUID4(payload.id_)
            if payload.created_at:
                entity.created_at = from_str_to_dt(
                    str_time=payload.created_at, format_=DATETIME_DEFAULT_FORMAT
                )

            new_id = await session.create(entity=entity)

            return await session.get_by_id(id_=new_id)
        except Exception as exc:
            logger.error(exc)
            raise CreateCommentException(exc)

    async def get_by_id(
        self, id_: str, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Optional[CommentEntity]:
        try:
            session = uow.comment_repo

            return await session.get_by_id(id_=UUID4(id_))
        except Exception as exc:
            logger.error(exc)
            raise GetCommentException(exc)

    async def get_multi(
        self,
        filter_: GetMultiCommentsFilter,
        uow: RelationalDBUnitOfWork,
    ) -> Tuple[List[CommentEntity], Optional[int]]:
        try:
            session = uow.comment_repo

            return await session.get_multi(filter_=filter_)
        except Exception as exc:
            logger.error(exc)
            raise GetCommentException(exc)

    async def update(
        self,
        payload: UpdateCommentPayload,
        uow: RelationalDBUnitOfWork,
    ):
        try:
            session = uow.comment_repo

            existed_comment = await session.get_by_id(id_=UUID4(payload.id_))
            if not existed_comment:
                raise Exception(f"Not found comment: {payload.id_}")

            if str(existed_comment.owner_id) != payload.owner_id:
                raise Exception(f"{payload.owner_id} is not owner of this comment")

            entity = CommentEntity(
                id_=UUID4(payload.id_),
                text_content=existed_comment.text_content,
                created_at=existed_comment.created_at,
                updated_at=datetime.now(tz=UTC),
                post_id=existed_comment.post_id,
                owner_id=existed_comment.owner_id,
            )
            if payload.text_content:
                entity.text_content = payload.text_content
            if payload.updated_at:
                entity.updated_at = from_str_to_dt(
                    str_time=payload.updated_at, format_=DATETIME_DEFAULT_FORMAT
                )

            await session.update(entity=entity)
        except Exception as exc:
            logger.error(exc)
            raise UpdateCommentException(exc)

    async def delete(
        self,
        payload: DeleteCommentPayload,
        uow: RelationalDBUnitOfWork,
    ):
        try:
            session = uow.comment_repo

            existed_comment = await session.get_by_id(id_=UUID4(payload.id_))
            if not existed_comment:
                raise Exception(f"Not found comment: {payload.id_}")

            if str(existed_comment.owner_id) != payload.owner_id:
                raise Exception(f"{payload.owner_id} is not owner of this comment")

            await session.delete(id_=UUID4(payload.id_))
        except Exception as exc:
            logger.error(exc)
            raise DeleteCommentException(exc)
