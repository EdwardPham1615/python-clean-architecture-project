from typing import Any, Optional

from pydantic import BaseModel

from internal.controllers.responses.error_code.common import common_internal_error
from internal.controllers.responses.success_code.common import server_ok


class MessageResponse(BaseModel):
    msg_code: str
    msg_name: str
    status_code: int


class DataResponse(BaseModel):
    data: Optional[Any] = None
    count: Optional[int] = None
    message: MessageResponse


class HealthState(BaseModel):
    app_status: DataResponse
    http_ready: bool = False
    grpc_ready: bool = False
    error_message: Optional[MessageResponse] = None

    def refresh(self) -> None:
        self._refresh()

    def set_http_ready(self, ready: bool) -> None:
        self.http_ready = ready
        self._refresh()

    def set_grpc_ready(self, ready: bool) -> None:
        self.grpc_ready = ready
        self._refresh()

    def mark_error(self, message: MessageResponse) -> None:
        self.error_message = message
        self._refresh()

    def _refresh(self) -> None:
        self.app_status.data = {"http": self.http_ready, "grpc": self.grpc_ready}
        if self.error_message is not None:
            self.app_status.message = self.error_message
            return
        serving = self.http_ready and self.grpc_ready
        self.app_status.message = server_ok if serving else common_internal_error
