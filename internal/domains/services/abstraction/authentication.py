import abc
from typing import Optional, Tuple

from fastapi import Request


class AbstractAuthenticationSVC(abc.ABC):
    @abc.abstractmethod
    async def get_certs(self) -> Tuple[Optional[dict], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def decode_token(
        self, token: str
    ) -> Tuple[Optional[dict], Optional[Exception]]:
        raise NotImplementedError

    @abc.abstractmethod
    async def handle_webhook_event(self, ctx_req_: Request) -> Optional[Exception]:
        raise NotImplementedError
