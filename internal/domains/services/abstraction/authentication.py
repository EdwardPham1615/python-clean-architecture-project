import abc
from typing import Optional, Tuple


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
    async def handle_webhook_event(self, event: dict) -> Optional[Exception]:
        raise NotImplementedError
