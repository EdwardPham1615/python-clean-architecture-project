from fastapi import status

from internal.controllers.responses import MessageResponse

create_post_fail = MessageResponse(
    msg_code="E101",
    msg_name="Create post fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
get_post_fail = MessageResponse(
    msg_code="E102",
    msg_name="Get post fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
update_post_fail = MessageResponse(
    msg_code="E103",
    msg_name="Update post fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
delete_post_fail = MessageResponse(
    msg_code="E104",
    msg_name="Delete post fail",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
