import abc
from typing import Optional, Tuple

from internal.domains.entities import CreateUserPayload, UpdateUserPayload, UserEntity


class AbstractUserSVC(abc.ABC):
    @abc.abstractmethod
    async def create(
        self, payload: CreateUserPayload
    ) -> Tuple[Optional[UserEntity], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: str
    ) -> Tuple[Optional[UserEntity], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, payload: UpdateUserPayload) -> Optional[Exception]:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id_: str) -> Optional[Exception]:
        raise NotImplementedError
