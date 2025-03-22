from typing import Optional

from pydantic import BaseModel

from internal.domains.entities import CommentEntity
from utils.time_utils import from_dt_to_str, DATETIME_DEFAULT_FORMAT


class CreateCommentResourceV1(BaseModel):
    id_: Optional[str] = None
    text_content: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    post_id: Optional[str] = None

    def from_entity(self, entity: CommentEntity):
        self.id_ = str(entity.id_)
        self.text_content = entity.text_content
        self.created_at = from_dt_to_str(
            dt=entity.created_at, format_=DATETIME_DEFAULT_FORMAT
        )
        if entity.updated_at:
            self.updated_at = from_dt_to_str(
                dt=entity.updated_at, format_=DATETIME_DEFAULT_FORMAT
            )
        self.post_id = str(entity.post_id)
        return self


class GetCommentResourceV1(BaseModel):
    id_: Optional[str] = None
    text_content: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    post_id: Optional[str] = None

    def from_entity(self, entity: CommentEntity):
        self.id_ = str(entity.id_)
        self.text_content = entity.text_content
        self.created_at = from_dt_to_str(
            dt=entity.created_at, format_=DATETIME_DEFAULT_FORMAT
        )
        if entity.updated_at:
            self.updated_at = from_dt_to_str(
                dt=entity.updated_at, format_=DATETIME_DEFAULT_FORMAT
            )
        self.post_id = str(entity.post_id)
        return self
