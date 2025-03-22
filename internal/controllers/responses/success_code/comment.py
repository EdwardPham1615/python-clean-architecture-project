from fastapi import status

from internal.controllers.responses import MessageResponse

create_comment_success = MessageResponse(
    msg_code="S201",
    msg_name="Create comment success",
    status_code=status.HTTP_201_CREATED,
)
get_comment_success = MessageResponse(
    msg_code="S202", msg_name="Get comment success", status_code=status.HTTP_200_OK
)
update_comment_success = MessageResponse(
    msg_code="S203", msg_name="Update comment success", status_code=status.HTTP_200_OK
)
delete_comment_success = MessageResponse(
    msg_code="S204", msg_name="Delete comment success", status_code=status.HTTP_200_OK
)
