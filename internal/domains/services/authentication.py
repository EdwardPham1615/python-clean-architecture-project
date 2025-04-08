from typing import Optional, Tuple

from loguru import logger

from internal.domains.entities import WebhookEventPayload
from internal.domains.services.abstraction import AbstractAuthenticationSVC
from internal.domains.usecases.abstraction import AbstractUserUC
from internal.infrastructures.external_authentication_service.abstraction import (
    AbstractExternalAuthenticationSVC,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)


class AuthenticationSVC(AbstractAuthenticationSVC):
    def __init__(
        self,
        external_authentication_svc: AbstractExternalAuthenticationSVC,
        relational_db_uow: RelationalDBUnitOfWork,
        user_uc: AbstractUserUC,
    ):
        self._external_authentication_svc = external_authentication_svc
        self._relational_db_uow = relational_db_uow
        self._user_uc = user_uc

    async def get_certs(self) -> Tuple[Optional[dict], Optional[Exception]]:
        try:
            certs = await self._external_authentication_svc.get_certs()
        except Exception as exc:
            logger.error(exc)
            error = exc
            return None, error

        return certs, None

    async def decode_token(
        self, token: str
    ) -> Tuple[Optional[dict], Optional[Exception]]:
        try:
            token_payload = await self._external_authentication_svc.decode_token(token)
        except Exception as exc:
            logger.error(exc)
            error = exc
            return None, error

        return token_payload, None

    async def handle_webhook_event(self, event: dict) -> Optional[Exception]:
        pass
