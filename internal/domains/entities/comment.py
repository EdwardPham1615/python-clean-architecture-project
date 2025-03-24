from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, ValidationError

from internal.domains.entities.post import PostEntity
from utils.time_utils import DATETIME_DEFAULT_FORMAT, from_str_to_dt


class CommentEntity(BaseModel):
    id_: UUID4
    text_content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    post_id: UUID4
    post: Optional[PostEntity] = None
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    def to_dict(self, exclude_none: bool = False) -> dict:
        return self.model_dump(exclude_none=exclude_none)


class GetMultiCommentsFilter(BaseModel):
    sort_field: Optional[str] = None
    sort_order: Optional[str] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    enable_count: Optional[bool] = None
    post_id: Optional[str] = None

    def validate_(self):
        if self.sort_order:
            if self.sort_order not in ["DESC", "ASC"]:
                raise ValidationError(f"Invalid sort order: {self.sort_order}")

        if self.from_date:
            try:
                from_str_to_dt(str_time=self.from_date, format_=DATETIME_DEFAULT_FORMAT)
            except Exception as exc:
                raise ValidationError(exc)

        if self.to_date:
            try:
                from_str_to_dt(str_time=self.to_date, format_=DATETIME_DEFAULT_FORMAT)
            except Exception as exc:
                raise ValidationError(exc)

        if self.post_id:
            try:
                UUID4(self.post_id)
            except Exception as exc:
                raise ValidationError(exc)


class CreateCommentPayload(BaseModel):
    id_: Optional[str] = None
    text_content: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    post_id: Optional[str] = None

    def validate_(self):
        if self.id_:
            try:
                UUID4(self.id_)
            except Exception as exc:
                raise ValidationError(exc)
        if self.created_at:
            try:
                from_str_to_dt(
                    str_time=self.created_at, format_=DATETIME_DEFAULT_FORMAT
                )
            except Exception as exc:
                raise ValidationError(exc)
        if self.updated_at:
            try:
                from_str_to_dt(
                    str_time=self.updated_at, format_=DATETIME_DEFAULT_FORMAT
                )
            except Exception as exc:
                raise ValidationError(exc)
        if self.post_id:
            try:
                UUID4(self.post_id)
            except Exception as exc:
                raise ValidationError(exc)


class UpdateCommentPayload(BaseModel):
    id_: Optional[str] = None
    text_content: Optional[str] = None
    updated_at: Optional[str] = None

    def validate_(self):
        if self.id_:
            try:
                UUID4(self.id_)
            except Exception as exc:
                raise ValidationError(exc)
        if self.updated_at:
            try:
                from_str_to_dt(
                    str_time=self.updated_at, format_=DATETIME_DEFAULT_FORMAT
                )
            except Exception as exc:
                raise ValidationError(exc)
