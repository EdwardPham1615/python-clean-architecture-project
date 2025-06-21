from fastapi import status

from internal.controllers.responses import MessageResponse

server_ok = MessageResponse(
    msg_code="S001", msg_name="Server status ok", status_code=status.HTTP_200_OK
)
