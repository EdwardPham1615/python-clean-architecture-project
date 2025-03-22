from fastapi import status

from internal.controllers.responses import MessageResponse

create_post_success = MessageResponse(
    msg_code="S101", msg_name="Create post success", status_code=status.HTTP_201_CREATED
)
get_post_success = MessageResponse(
    msg_code="S102", msg_name="Get post success", status_code=status.HTTP_200_OK
)
update_post_success = MessageResponse(
    msg_code="S103", msg_name="Update post success", status_code=status.HTTP_200_OK
)
delete_post_success = MessageResponse(
    msg_code="S104", msg_name="Delete post success", status_code=status.HTTP_200_OK
)
