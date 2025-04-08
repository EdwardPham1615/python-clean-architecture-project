from fastapi import status

from internal.controllers.responses import MessageResponse

sync_webhook_event_success = MessageResponse(
    msg_code="S301",
    msg_name="Sync webhook event success",
    status_code=status.HTTP_200_OK,
)
