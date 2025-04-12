import abc

from fastapi import Request

from internal.domains.entities import WebhookEventEntity
from internal.infrastructures.external_authentication_service.abstraction import (
    AbstractExternalAuthenticationSVC,
)


class AbstractAuthenticationUC(abc.ABC):
    external_authentication_svc: AbstractExternalAuthenticationSVC

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
