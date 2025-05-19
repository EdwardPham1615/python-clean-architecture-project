from typing import Optional

from pydantic import UUID4
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from internal.domains.entities import UserEntity
from internal.infrastructures.relational_db.abstraction import AbstractUserRepo
from internal.infrastructures.relational_db.postgres.models import User, UserModelMapper


class UserRepo(AbstractUserRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sort_fields = {
            "created_at": User.created_at,
            "updated_at": User.updated_at,
        }

    async def create(self, entity: UserEntity) -> UUID4:
        obj_in_data = entity.to_dict()
        stmt = insert(User).values(**obj_in_data).returning(User.id_)
        result = await self.session.execute(stmt)
        new_id = result.scalar()
        return new_id

    async def get_by_id(self, id_: UUID4) -> Optional[UserEntity]:
        stmt = select(User).filter(User.id_ == id_)
        token_ = (await self.session.execute(stmt)).scalars().first()
        if not token_:
            return None
        return UserModelMapper.to_entity(model=token_)

    async def update(self, entity: UserEntity):
        obj_in_data = entity.to_dict()
        stmt = update(User).where(User.id_ == entity.id_).values(**obj_in_data)
        await self.session.execute(stmt)
        return

    async def delete(self, id_: UUID4):
        stmt = delete(User).where(User.id_ == id_)
        await self.session.execute(stmt)
        return
