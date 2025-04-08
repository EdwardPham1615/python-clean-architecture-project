from fastapi import status

from internal.controllers.responses import MessageResponse

sync_webhook_event_fail = MessageResponse(
    msg_code="E301",
    msg_name="Sync webhook event fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
