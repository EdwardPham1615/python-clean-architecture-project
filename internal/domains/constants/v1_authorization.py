from enum import Enum


class V1ReBACObjectType(str, Enum):
    USER = "user"
    POST = "post"
    COMMENT = "comment"


class V1ReBACRelation(str, Enum):
    IS_SUPER_ADMIN = "is_super_admin"
    IS_OWNER = "is_owner"
    CAN_CREATE = "can_create"
    CAN_GET_DETAIL = "can_get_detail"
    CAN_GET_LIST = "can_get_list"
    CAN_UPDATE = "can_update"
    CAN_DELETE = "can_delete"
