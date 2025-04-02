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
common_missing_or_invalid_token_error = MessageResponse(
    msg_code="E003",
    msg_name="Missing or invalid token",
    status_code=status.HTTP_401_UNAUTHORIZED,
)
common_token_expired_error = MessageResponse(
    msg_code="E004",
    msg_name="Token Expired",
    status_code=status.HTTP_401_UNAUTHORIZED,
)
common_invalid_token_error = MessageResponse(
    msg_code="E005",
    msg_name="Invalid token",
    status_code=status.HTTP_401_UNAUTHORIZED,
)
