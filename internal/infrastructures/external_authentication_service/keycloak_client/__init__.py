from typing import Optional

from keycloak import KeycloakAdmin, KeycloakOpenID, KeycloakOpenIDConnection

from internal.infrastructures.external_authentication_service.abstraction import (
    AbstractExternalAuthenticationSVC,
)


class KeycloakClient(AbstractExternalAuthenticationSVC):
    def __init__(
        self,
        url: str,
        admin_username: str,
        admin_password: str,
        realm: str,
        client_id: str,
        client_secret: str,
    ):
        self._url = url
        self._admin_username = admin_username
        self._admin_password = admin_password
        self._realm = realm
        self._client_id = client_id
        self._client_secret = client_secret
        self._certs: Optional[dict] = None

        self._openid = KeycloakOpenID(
            server_url=url,
            realm_name=realm,
            client_id=client_id,
            client_secret_key=client_secret,
        )

        self._connection = KeycloakOpenIDConnection(
            server_url=url,
            username=admin_username,
            password=admin_password,
            realm_name="master",
            user_realm_name=realm,
            client_id=client_id,
            client_secret_key=client_secret,
            verify=True,
        )

        self._admin = KeycloakAdmin(connection=self._connection)

    async def get_certs(self) -> dict:
        if not self._certs:
            self._certs = await self._openid.a_certs()
        return self._certs

    async def decode_token(self, token: str) -> Optional[dict]:
        return await self._openid.a_decode_token(token=token, validate=True)
