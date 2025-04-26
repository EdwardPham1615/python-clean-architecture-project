from starlette.requests import Request

from internal.domains.entities import WebhookEventEntity
from internal.domains.errors import (
    CheckWebhookAuthenticationException,
    DecodeTokenException,
    GetCertsException,
    ParseWebhookEventException,
)
from internal.domains.usecases.abstraction import AbstractAuthenticationUC
from internal.infrastructures.external_authentication_service.abstraction import (
    AbstractExternalAuthenticationSVC,
)
from utils.logger_utils import get_shared_logger

logger = get_shared_logger()


class AuthenticationUC(AbstractAuthenticationUC):
    def __init__(self, external_authentication_svc: AbstractExternalAuthenticationSVC):
        self._external_authentication_svc = external_authentication_svc

    async def get_certs(self) -> dict:
        try:
            certs = await self._external_authentication_svc.get_certs()
            return certs
        except Exception as exc:
            logger.error(exc)
            raise GetCertsException(exc)

    async def decode_token(self, token: str) -> dict:
        try:
            token_payload = await self._external_authentication_svc.decode_token(token)
            return token_payload
        except Exception as exc:
            logger.error(exc)
            raise DecodeTokenException(exc)

    async def check_webhook_authentication(self, ctx_req_: Request) -> bool:
        try:
            is_valid = (
                await self._external_authentication_svc.check_webhook_authentication(
                    ctx_req_=ctx_req_
                )
            )
            return is_valid
        except Exception as exc:
            logger.error(exc)
            raise CheckWebhookAuthenticationException(exc)

    async def parse_webhook_event(self, event: dict) -> WebhookEventEntity:
        try:
            entity = await self._external_authentication_svc.parse_webhook_event(
                event=event
            )
            return entity
        except Exception as exc:
            logger.error(exc)
            raise ParseWebhookEventException(exc)
