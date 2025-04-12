import abc
from typing import Any, List, Optional, Tuple

from internal.domains.entities import PermEntity


class AbstractExternalReBACAuthorizationSVC(abc.ABC):
    url: str
    api_token: str
    store_id: str
    authorization_model_id: str
    timeout_in_millis: Optional[int] = None

    @abc.abstractmethod
    async def create_perms(
        self, entities: List[PermEntity]
    ) -> Tuple[Optional[Any], Optional[Exception]]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def check_single_perm(
        self, entity: PermEntity
    ) -> Tuple[Optional[bool], Optional[Exception]]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def check_perms(
        self, entities: List[PermEntity]
    ) -> Tuple[Optional[bool], Optional[Exception]]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete_perms(
        self, entities: List[PermEntity]
    ) -> Tuple[Optional[Any], Optional[Exception]]:
        raise NotImplementedError()
