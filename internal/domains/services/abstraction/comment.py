import abc
from typing import Tuple, Optional, List

from internal.domains.entities import (
    CreateCommentPayload,
    CommentEntity,
    GetMultiCommentsFilter,
    UpdateCommentPayload,
)


class AbstractCommentSVC(abc.ABC):
    @abc.abstractmethod
    async def create(
        self, payload: CreateCommentPayload
    ) -> Tuple[Optional[CommentEntity], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, id_: str
    ) -> Tuple[Optional[CommentEntity], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_multi(
        self, filter_: GetMultiCommentsFilter
    ) -> Tuple[Tuple[List[CommentEntity], Optional[int]], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, payload: UpdateCommentPayload) -> Optional[Exception]:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, id_: str) -> Optional[Exception]:
        raise NotImplementedError
