import hashlib
import hmac
from datetime import UTC, datetime
from typing import Optional, Tuple, Union

from fastapi import Request
from keycloak import KeycloakAdmin, KeycloakOpenID, KeycloakOpenIDConnection
from loguru import logger

from internal.domains.constants import WebhookEventOperation, WebhookEventResource
from internal.domains.entities import (
    WebhookEventActionByEntity,
    WebhookEventEntity,
    WebhookEventResourceUserDetails,
)
from internal.infrastructures.external_authentication_service.abstraction import (
    AbstractExternalAuthenticationSVC,
)
from utils.string_utils import from_str_to_dict
from utils.time_utils import from_timestamp_to_dt


class KeycloakClient(AbstractExternalAuthenticationSVC):
    def __init__(
        self,
        url: str,
        admin_username: str,
        admin_password: str,
        realm: str,
        client_id: str,
        client_secret: str,
        webhook_secret: str,
    ):
        self._url = url
        self._admin_username = admin_username
        self._admin_password = admin_password
        self._realm = realm
        self._client_id = client_id
        self._client_secret = client_secret
        self._webhook_secret = webhook_secret
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

    async def check_webhook_authentication(self, ctx_req_: Request) -> bool:
        x_keycloak_signature = ctx_req_.headers.get("X-Keycloak-Signature", None)
        if not x_keycloak_signature:
            return False

        raw_body = await ctx_req_.body()
        # Compute HMAC using the shared secret
        computed_signature = hmac.new(
            self._webhook_secret.encode("utf-8"), raw_body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(computed_signature, x_keycloak_signature):
            return False

        return True

    async def parse_webhook_event(self, event: dict) -> WebhookEventEntity:
        realm_name = event.get("realmName", "")
        if realm_name == "":
            raise Exception("Not found realmName")

        raw_operation = event.get("operationType", None)
        if not raw_operation:
            raise Exception("Not found operationType")

        operation: WebhookEventOperation
        if raw_operation == "CREATE":
            operation = WebhookEventOperation.CREATE
        elif raw_operation == "UPDATE":
            operation = WebhookEventOperation.UPDATE
        elif raw_operation == "DELETE":
            operation = WebhookEventOperation.DELETE
        else:
            logger.debug(f"Unsupported operationType: {raw_operation}")
            return None

        action_at = datetime.now(tz=UTC)
        raw_time = event.get("time", 0)
        if raw_time != 0:
            action_at = from_timestamp_to_dt(
                timestamp=int(raw_time),
                unit=1000,  # millis
                with_tz=True,
            )

        auth_details = event.get("authDetails", {})
        if auth_details == {}:
            raise Exception("Not found authDetails")
        action_by_user_id = auth_details.get("userId", "")
        if action_by_user_id == "":
            raise Exception("Not found userId")
        action_by_username = auth_details.get("username", "")
        if action_by_username == "":
            raise Exception("Not found username")
        action_by_realm_id = auth_details.get("realmId", "")
        if action_by_realm_id == "":
            raise Exception("Not found realmId")
        action_by_client_id = auth_details.get("clientId", "")
        if action_by_client_id == "":
            raise Exception("Not found clientId")
        action_by_ip_address = auth_details.get("ipAddress", None)

        representation = event.get("representation", "")
        json_representation = {}
        if representation != "":
            json_representation = from_str_to_dict(json_str=representation)

        raw_details = event.get("details", {})

        resource: WebhookEventResource
        resource_detail: Optional[Union[WebhookEventResourceUserDetails]] = None
        resource_type = event.get("resourceType", "")
        if resource_type == "":
            raise Exception("Not found resourceType")
        if resource_type == "USER":
            resource = WebhookEventResource.USER
            resource_detail = WebhookEventResourceUserDetails()
            resource_detail.id_ = json_representation.get("id", None)
            if not resource_detail.id_:
                resource_detail.id_ = raw_details.get("userId", None)
            resource_detail.username = json_representation.get("username", None)
            if not resource_detail.username:
                resource_detail.username = raw_details.get("username", None)
            resource_detail.first_name = json_representation.get("firstName", None)
            resource_detail.last_name = json_representation.get("lastName", None)
            resource_detail.email = json_representation.get("email", None)
            created_timestamp = json_representation.get("createdTimestamp", 0)
            if created_timestamp != 0:
                resource_detail.created_at = from_timestamp_to_dt(
                    timestamp=int(created_timestamp),
                    unit=1000,  # millis
                    with_tz=True,
                )
            resource_detail.is_active = json_representation.get("enabled", None)
        else:
            raise Exception(f"Unsupported resourceType: {resource_type}")

        if not resource_detail:
            raise Exception("Cannot parse resource_detail")

        event_payload = WebhookEventEntity(
            realm_name=realm_name,
            operation=operation,
            action_by=WebhookEventActionByEntity(
                id_=action_by_user_id,
                username=action_by_username,
                realm_id=action_by_realm_id,
                client_id=action_by_client_id,
                ip_address=action_by_ip_address,
            ),
            action_at=action_at,
            resource=resource,
            resource_detail=resource_detail,
        )
        return event_payload
