from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict


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
