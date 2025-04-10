from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, ValidationError

from utils.time_utils import DATETIME_DEFAULT_FORMAT, from_str_to_dt


class UserEntity(BaseModel):
    id_: UUID4
    username: str
    metadata_: Optional[dict] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

    def to_dict(self, exclude_none: bool = False) -> dict:
        return self.model_dump(exclude_none=exclude_none)


class UserMetadataPayload(BaseModel):
    fullname: Optional[str] = None
    dob: Optional[str] = None

    def to_dict(self, exclude_none: bool = False) -> dict:
        return self.model_dump(exclude_none=exclude_none)


class CreateUserPayload(BaseModel):
    id_: Optional[str] = None
    username: Optional[str] = None
    metadata_: Optional[UserMetadataPayload] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

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


class UpdateUserPayload(BaseModel):
    id_: Optional[str] = None
    metadata_: Optional[UserMetadataPayload] = None
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
