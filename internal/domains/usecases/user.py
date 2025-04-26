import uuid
from datetime import UTC, datetime
from typing import Optional

from pydantic import UUID4

from internal.domains.entities import CreateUserPayload, UpdateUserPayload, UserEntity
from internal.domains.errors import (
    CreateUserException,
    DeleteUserException,
    GetUserException,
    UpdateUserException,
)
from internal.domains.usecases.abstraction import AbstractUserUC
from internal.infrastructures.relational_db.abstraction import (
    AbstractUserRepo as RelationalDBAbstractUserRepo,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)
from utils.logger_utils import get_shared_logger
from utils.time_utils import DATETIME_DEFAULT_FORMAT, from_str_to_dt

logger = get_shared_logger()


class UserUC(AbstractUserUC):
    def __init__(self, relational_db_user_repo: RelationalDBAbstractUserRepo):
        self._relational_db_user_repo = relational_db_user_repo

    async def create(
        self, payload: CreateUserPayload, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Optional[UserEntity]:
        try:
            session = self._relational_db_user_repo
            if uow:
                session = uow.user_repo

            entity = UserEntity(
                id_=uuid.uuid4(),
                username=payload.username,
                is_active=True,
                created_at=datetime.now(tz=UTC),
            )
            if payload.id_:
                entity.id_ = UUID4(payload.id_)
            if payload.metadata_:
                entity.metadata_ = payload.metadata_.to_dict(exclude_none=True)
            if payload.created_at:
                entity.created_at = from_str_to_dt(
                    str_time=payload.created_at, format_=DATETIME_DEFAULT_FORMAT
                )

            new_id = await session.create(entity=entity)

            return await session.get_by_id(id_=new_id)
        except Exception as exc:
            logger.error(exc)
            raise CreateUserException(exc)

    async def get_by_id(
        self, id_: str, uow: Optional[RelationalDBUnitOfWork] = None
    ) -> Optional[UserEntity]:
        try:
            session = self._relational_db_user_repo
            if uow:
                session = uow.user_repo

            return await session.get_by_id(id_=UUID4(id_))
        except Exception as exc:
            logger.error(exc)
            raise GetUserException(exc)

    async def update(
        self, payload: UpdateUserPayload, uow: Optional[RelationalDBUnitOfWork] = None
    ):
        try:
            session = self._relational_db_user_repo
            if uow:
                session = uow.user_repo

            existed_user = await session.get_by_id(id_=UUID4(payload.id_))
            if not existed_user:
                raise Exception(f"Not found user: {payload.id_}")

            entity = UserEntity(
                id_=UUID4(payload.id_),
                username=existed_user.username,
                metadata_=existed_user.metadata_,
                is_active=existed_user.is_active,
                created_at=existed_user.created_at,
                updated_at=datetime.now(tz=UTC),
            )
            if payload.metadata_:
                entity.metadata_ = payload.metadata_.to_dict(exclude_none=True)
            if payload.updated_at:
                entity.updated_at = from_str_to_dt(
                    str_time=payload.updated_at, format_=DATETIME_DEFAULT_FORMAT
                )

            await session.update(entity=entity)
        except Exception as exc:
            logger.error(exc)
            raise UpdateUserException(exc)

    async def delete(self, id_: str, uow: Optional[RelationalDBUnitOfWork] = None):
        try:
            session = self._relational_db_user_repo
            if uow:
                session = uow.user_repo

            existed_user = await session.get_by_id(id_=UUID4(id_))
            if not existed_user:
                raise Exception(f"Not found user: {id_}")

            await session.delete(id_=UUID4(id_))
        except Exception as exc:
            logger.error(exc)
            raise DeleteUserException(exc)
