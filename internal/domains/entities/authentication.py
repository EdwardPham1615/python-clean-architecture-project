from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel

from internal.domains.constants import WebhookEventOperation, WebhookEventResource


class RealmAccess(BaseModel):
    roles: Optional[List[str]] = None


class ResourceAccessRoles(BaseModel):
    roles: Optional[List[str]] = None


class ResourceAccess(BaseModel):
    account: Optional[ResourceAccessRoles] = None


class JWTPayload(BaseModel):
    exp: Optional[int] = None  # Unix timestamp
    iat: Optional[int] = None  # Unix timestamp
    jti: Optional[str] = None
    iss: Optional[str] = None
    aud: Optional[str] = None
    sub: Optional[str] = None
    typ: Optional[str] = None
    azp: Optional[str] = None
    sid: Optional[str] = None
    acr: Optional[str] = None
    allowed_origins: Optional[List[str]] = None
    realm_access: Optional[RealmAccess] = None
    resource_access: Optional[ResourceAccess] = None
    scope: Optional[str] = None
    email_verified: Optional[bool] = None
    name: Optional[str] = None
    preferred_username: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    email: Optional[str] = None

    def get_exp_datetime(self) -> Optional[datetime]:
        return datetime.fromtimestamp(self.exp) if self.exp else None

    def get_iat_datetime(self) -> Optional[datetime]:
        return datetime.fromtimestamp(self.iat) if self.iat else None


class WebhookEventActionByPayload(BaseModel):
    id_: str
    username: str
    realm_id: str
    client_id: str
    ip_address: str


class WebhookEventResourceUserDetails(BaseModel):
    id_: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class WebhookEventPayload(BaseModel):
    realm_name: str
    operation: WebhookEventOperation
    action_by: WebhookEventActionByPayload
    action_at: datetime
    resource: WebhookEventResource
    resource_detail: Union[WebhookEventResourceUserDetails]
