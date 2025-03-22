import uuid
from datetime import datetime, UTC
from typing import Optional, Tuple, List

from loguru import logger
from pydantic import UUID4

from internal.domains.entities import (
    GetMultiPostsFilter,
    PostEntity,
    CreatePostPayload,
    UpdatePostPayload,
)
from internal.domains.errors import (
    CreatePostException,
    GetPostException,
    UpdatePostException,
    DeletePostException,
)
from internal.domains.usecases.abstraction import AbstractPostUC

from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)
from internal.infrastructures.relational_db.abstraction import (
    AbstractPostRepo as RelationalDBAbstractPostRepo,
)
from utils.time_utils import from_str_to_dt, DATETIME_DEFAULT_FORMAT


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

            entity = PostEntity(
                id_=UUID4(payload.id_),
                text_content=existed_post.text_content,
                created_at=existed_post.created_at,
                updated_at=datetime.now(tz=UTC),
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

    async def delete(self, id_: str, uow: Optional[RelationalDBUnitOfWork] = None):
        try:
            session = self._relational_db_post_repo
            if uow:
                session = uow.post_repo

            existed_post = await session.get_by_id(id_=UUID4(id_))
            if not existed_post:
                raise Exception(f"Not found post: {id_}")

            await session.delete(id_=UUID4(id_))
        except Exception as exc:
            logger.error(exc)
            raise DeletePostException(exc)
