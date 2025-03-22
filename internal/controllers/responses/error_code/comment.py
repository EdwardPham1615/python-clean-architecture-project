from fastapi import status

from internal.controllers.responses import MessageResponse

create_comment_fail = MessageResponse(
    msg_code="E201",
    msg_name="Create comment fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
get_comment_fail = MessageResponse(
    msg_code="E202",
    msg_name="Get comment fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
update_comment_fail = MessageResponse(
    msg_code="E203",
    msg_name="Update comment fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
delete_comment_fail = MessageResponse(
    msg_code="E204",
    msg_name="Delete comment fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
