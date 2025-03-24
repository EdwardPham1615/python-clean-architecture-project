import uuid

from sqlalchemy import UUID, Column, Text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP

from internal.domains.entities import PostEntity
from internal.infrastructures.relational_db.base import Base


class Post(Base):
    __tablename__ = "posts"
    id_ = Column("id", UUID, primary_key=True, default=uuid.uuid4)
    text_content = Column("text_content", Text)
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column("updated_at", TIMESTAMP(timezone=True), onupdate=func.now())


class PostModelMapper:
    @staticmethod
    def to_entity(model: Post) -> PostEntity:
        return PostEntity.model_validate(obj=model)
