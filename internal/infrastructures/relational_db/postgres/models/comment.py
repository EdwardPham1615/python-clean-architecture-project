import uuid

from sqlalchemy import UUID, Column, Text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP

from internal.domains.entities import CommentEntity
from internal.infrastructures.relational_db.base import Base


class Comment(Base):
    __tablename__ = "comments"
    id_ = Column("id", UUID, primary_key=True, default=uuid.uuid4)
    text_content = Column("text_content", Text)
    created_at = Column(
        "created_at", TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at = Column("updated_at", TIMESTAMP(timezone=True), onupdate=func.now())

    # fk
    post_id = Column("post_id", UUID, nullable=False)
    owner_id = Column("owner_id", UUID, nullable=False)


class CommentModelMapper:
    @staticmethod
    def to_entity(model: Comment) -> CommentEntity:
        return CommentEntity.model_validate(obj=model)
