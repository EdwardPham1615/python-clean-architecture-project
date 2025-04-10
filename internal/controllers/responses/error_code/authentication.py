from fastapi import status

from internal.controllers.responses import MessageResponse

sync_webhook_event_fail = MessageResponse(
    msg_code="E301",
    msg_name="Sync webhook event fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
invalid_webhook_secret_error = MessageResponse(
    msg_code="E302",
    msg_name="Invalid webhook secret",
    status_code=status.HTTP_401_UNAUTHORIZED,
)
