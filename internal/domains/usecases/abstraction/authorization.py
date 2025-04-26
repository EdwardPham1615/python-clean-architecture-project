import abc
from typing import List

from internal.domains.entities import PermEntity
from internal.infrastructures.external_rebac_authorization_service.abstraction import (
    AbstractExternalReBACAuthorizationSVC,
)


class AbstractAuthorizationUC(abc.ABC):
    external_authorization_svc: AbstractExternalReBACAuthorizationSVC

    @abc.abstractmethod
    async def create_perms(self, entities: List[PermEntity]):
        raise NotImplementedError()

    @abc.abstractmethod
    async def check_single_perm(self, entity: PermEntity) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    async def check_perms(self, entities: List[PermEntity]) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete_perms(self, entities: List[PermEntity]):
        raise NotImplementedError()
