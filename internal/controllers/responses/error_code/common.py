from fastapi import status

from internal.controllers.responses import MessageResponse

common_internal_error = MessageResponse(
    msg_code="E001",
    msg_name="Internal Error",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
common_validation_error = MessageResponse(
    msg_code="E002",
    msg_name="Validation Error",
    status_code=status.HTTP_400_BAD_REQUEST,
)
