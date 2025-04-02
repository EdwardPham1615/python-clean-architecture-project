import abc


class AuthenticationService(abc.ABC):
    url: str
    admin_username: str
    admin_password: str
    realm: str
    client_id: str
    client_secret: str

    @abc.abstractmethod
    async def get_certs(self) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    async def decode_token(self, token: str) -> dict:
        raise NotImplementedError
