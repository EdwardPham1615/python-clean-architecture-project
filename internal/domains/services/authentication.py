from typing import Optional, Tuple

from loguru import logger

from internal.domains.constants import WebhookEventOperation, WebhookEventResource
from internal.domains.entities import CreateUserPayload, WebhookEventPayload
from internal.domains.entities.user import UpdateUserPayload, UserMetadataPayload
from internal.domains.services.abstraction import AbstractAuthenticationSVC
from internal.domains.usecases.abstraction import AbstractUserUC
from internal.infrastructures.external_authentication_service.abstraction import (
    AbstractExternalAuthenticationSVC,
)
from internal.infrastructures.relational_db.patterns import (
    AbstractUnitOfWork as RelationalDBUnitOfWork,
)
from utils.time_utils import DATETIME_DEFAULT_FORMAT, from_dt_to_str


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
        logger.debug(f"Received webhook event: {event}")

        event_payload: Optional[WebhookEventPayload] = None
        (
            event_payload,
            error,
        ) = await self._external_authentication_svc.parse_webhook_event(event=event)
        if error:
            return error

        logger.debug(f"Parsed webhook event: {event_payload}")

        try:
            if event_payload.resource == WebhookEventResource.USER:
                if not event_payload.resource_detail.id_:
                    raise Exception("Not found user id from resource detail")

                first_name = event_payload.resource_detail.first_name
                if not first_name:
                    first_name = ""
                last_name = event_payload.resource_detail.last_name
                if not last_name:
                    last_name = ""

                if event_payload.operation == WebhookEventOperation.CREATE:
                    if not event_payload.resource_detail.username:
                        raise Exception("Not found username from resource detail")

                    create_user_payload = CreateUserPayload(
                        id_=event_payload.resource_detail.id_,
                        username=event_payload.resource_detail.username,
                        metadata_=UserMetadataPayload(
                            fullname=first_name + " " + last_name,
                        ),
                        created_at=from_dt_to_str(
                            dt=event_payload.action_at, format_=DATETIME_DEFAULT_FORMAT
                        ),
                    )
                    create_user_payload.validate_()
                    async with self._relational_db_uow as session:
                        await self._user_uc.create(
                            payload=create_user_payload, uow=session
                        )
                elif event_payload.operation == WebhookEventOperation.UPDATE:
                    update_user_payload = UpdateUserPayload(
                        id_=event_payload.resource_detail.id_,
                        metadata_=UserMetadataPayload(
                            fullname=first_name + " " + last_name,
                        ),
                        updated_at=from_dt_to_str(
                            dt=event_payload.action_at, format_=DATETIME_DEFAULT_FORMAT
                        ),
                    )
                    async with self._relational_db_uow as session:
                        await self._user_uc.update(
                            payload=update_user_payload, uow=session
                        )
                elif event_payload.operation == WebhookEventOperation.DELETE:
                    async with self._relational_db_uow as session:
                        await self._user_uc.delete(
                            id_=event_payload.resource_detail.id_, uow=session
                        )
        except Exception as exc:
            logger.error(exc)
            error = exc
            return error

        return None
