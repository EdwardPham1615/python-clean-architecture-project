from typing import Any, List

from loguru import logger

from internal.domains.entities import PermEntity
from internal.domains.errors import (
    CheckPermException,
    CreatePermException,
    DeletePermException,
)
from internal.domains.usecases.abstraction import AbstractAuthorizationUC
from internal.infrastructures.external_rebac_authorization_service.abstraction import (
    AbstractExternalReBACAuthorizationSVC,
)


class AuthorizationUC(AbstractAuthorizationUC):
    def __init__(
        self, external_authorization_svc: AbstractExternalReBACAuthorizationSVC
    ):
        self._external_authorization_svc = external_authorization_svc

    async def create_perms(self, entities: List[PermEntity]):
        try:
            response = await self._external_authorization_svc.create_perms(
                entities=entities
            )
            for res in response:
                if res["success"] is False:
                    raise Exception("Create perm fail")
                if res["error"] is not None:
                    raise Exception(res["error"])
        except Exception as exc:
            logger.error(exc)
            raise CreatePermException(exc)

    async def check_single_perm(self, entity: PermEntity) -> bool:
        try:
            is_valid = await self._external_authorization_svc.check_single_perm(
                entity=entity
            )
            return is_valid
        except Exception as exc:
            logger.error(exc)
            raise CheckPermException(exc)

    async def check_perms(self, entities: List[PermEntity]) -> Any:
        try:
            is_valid = await self._external_authorization_svc.check_perms(
                entities=entities
            )
            return is_valid
        except Exception as exc:
            logger.error(exc)
            raise CheckPermException(exc)

    async def delete_perms(self, entities: List[PermEntity]):
        try:
            response = await self._external_authorization_svc.delete_perms(
                entities=entities
            )
            for res in response:
                if res["success"] is False:
                    raise Exception("Create perm fail")
                if res["error"] is not None:
                    raise Exception(res["error"])
        except Exception as exc:
            logger.error(exc)
            raise DeletePermException(exc)
