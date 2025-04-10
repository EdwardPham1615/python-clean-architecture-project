import enum


class WebhookEventOperation(enum.Enum):
    CREATE = 0
    UPDATE = 1
    DELETE = 2


class WebhookEventResource(enum.Enum):
    USER = 0
