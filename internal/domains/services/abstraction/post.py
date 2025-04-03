import abc
from typing import List, Optional, Tuple

from internal.domains.entities import (
    CreatePostPayload,
    DeletePostPayload,
    GetMultiPostsFilter,
    PostEntity,
    UpdatePostPayload,
)


class AbstractPostSVC(abc.ABC):
    @abc.abstractmethod
    async def create(
        self, payload: CreatePostPayload
    ) -> Tuple[Optional[PostEntity], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: str
    ) -> Tuple[Optional[PostEntity], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_multi(
        self, filter_: GetMultiPostsFilter
    ) -> Tuple[Tuple[List[PostEntity], Optional[int]], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, payload: UpdatePostPayload) -> Optional[Exception]:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, payload: DeletePostPayload) -> Optional[Exception]:
        raise NotImplementedError
