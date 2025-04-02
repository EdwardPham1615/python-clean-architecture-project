from sqlalchemy import UUID, VARCHAR, Boolean, Column, func
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP

from internal.domains.entities import UserEntity
from internal.infrastructures.relational_db.base import Base


class User(Base):
    __tablename__ = "users"
    id_ = Column("id", UUID, primary_key=True)
    username = Column("username", VARCHAR(256), nullable=False, unique=True)
    metadata_ = Column("metadata", JSONB)
    is_active = Column("is_active", Boolean, default=True)
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column("updated_at", TIMESTAMP(timezone=True), onupdate=func.now())


class UserModelMapper:
    @staticmethod
    def to_entity(model: User) -> UserEntity:
        return UserEntity.model_validate(obj=model)
