import abc

from fastapi import Request

from internal.domains.entities import WebhookEventEntity


class AbstractExternalAuthenticationSVC(abc.ABC):
    url: str
    admin_username: str
    admin_password: str
    realm: str
    client_id: str
    client_secret: str
    webhook_secret: str

    @abc.abstractmethod
    async def get_certs(self) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    async def decode_token(self, token: str) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    async def check_webhook_authentication(self, ctx_req_: Request) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def parse_webhook_event(self, event: dict) -> WebhookEventEntity:
        raise NotImplementedError
