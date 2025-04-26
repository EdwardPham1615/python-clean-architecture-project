import uuid
from datetime import UTC, datetime
from typing import List, Optional, Tuple

from loguru import logger
from pydantic import UUID4

from internal.domains.entities import (
    CreatePostPayload,
    DeletePostPayload,
    GetMultiPostsFilter,
    PostEntity,
    UpdatePostPayload,
)
from internal.domains.errors import (
    CreatePostException,
    DeletePostException,
    GetPostException,
    UpdatePostException,
)
from internal.domains.usecases.abstraction import AbstractPostUC
from internal.infrastructures.relational_db.abstraction import (
    AbstractPostRepo as RelationalDBAbstractPostRepo,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)
from utils.time_utils import DATETIME_DEFAULT_FORMAT, from_str_to_dt


class PostUC(AbstractPostUC):
    def __init__(self, relational_db_post_repo: RelationalDBAbstractPostRepo):
        self._relational_db_post_repo = relational_db_post_repo

    async def create(
        self, payload: CreatePostPayload, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Optional[PostEntity]:
        try:
            session = self._relational_db_post_repo
            if uow:
                session = uow.post_repo

            entity = PostEntity(
                id_=uuid.uuid4(),
                text_content=payload.text_content,
                created_at=datetime.now(tz=UTC),
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
            raise CreatePostException(exc)

    async def get_by_id(
        self, id_: str, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Optional[PostEntity]:
        try:
            session = self._relational_db_post_repo
            if uow:
                session = uow.post_repo

            return await session.get_by_id(id_=UUID4(id_))
        except Exception as exc:
            logger.error(exc)
            raise GetPostException(exc)

    async def get_multi(
        self, filter_: GetMultiPostsFilter, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Tuple[List[PostEntity], Optional[int]]:
        try:
            session = self._relational_db_post_repo
            if uow:
                session = uow.post_repo

            return await session.get_multi(filter_=filter_)
        except Exception as exc:
            logger.error(exc)
            raise GetPostException(exc)

    async def update(
        self, payload: UpdatePostPayload, uow: Optional[RelationalDBUnitOfWork] = None
    ):
        try:
            session = self._relational_db_post_repo
            if uow:
                session = uow.post_repo

            existed_post = await session.get_by_id(id_=UUID4(payload.id_))
            if not existed_post:
                raise Exception(f"Not found post: {payload.id_}")

            if str(existed_post.owner_id) != payload.owner_id:
                raise Exception(f"{payload.owner_id} is not owner of this post")

            entity = PostEntity(
                id_=UUID4(payload.id_),
                text_content=existed_post.text_content,
                created_at=existed_post.created_at,
                updated_at=datetime.now(tz=UTC),
                owner_id=existed_post.owner_id,
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
            raise UpdatePostException(exc)

    async def delete(
        self, payload: DeletePostPayload, uow: Optional[RelationalDBUnitOfWork] = None
    ):
        try:
            session = self._relational_db_post_repo
            if uow:
                session = uow.post_repo

            existed_post = await session.get_by_id(id_=UUID4(payload.id_))
            if not existed_post:
                raise Exception(f"Not found post: {payload.id_}")

            if str(existed_post.owner_id) != payload.owner_id:
                raise Exception(f"{payload.owner_id} is not owner of this post")

            await session.delete(id_=UUID4(payload.id_))
        except Exception as exc:
            logger.error(exc)
            raise DeletePostException(exc)
