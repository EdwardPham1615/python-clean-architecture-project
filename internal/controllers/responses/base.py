from typing import Any, Optional

from pydantic import BaseModel


class MessageResponse(BaseModel):
    msg_code: str
    msg_name: str
    status_code: int


class DataResponse(BaseModel):
    data: Optional[Any] = None
    count: Optional[int] = None
    message: MessageResponse
