from enum import Enum

from config import app_config


class SupportedAuthenticationService(str, Enum):
    KEYCLOAK = "keycloak"


AUTHENTICATION_SERVICE_VENDOR = app_config.authentication_service.vendor

if AUTHENTICATION_SERVICE_VENDOR == SupportedAuthenticationService.KEYCLOAK:
    from internal.infrastructures.external_authentication_service.keycloak_client import (
        KeycloakClient as ExternalAuthenticationServiceClient,
    )
else:
    raise RuntimeError(
        f"Invalid authentication service vendor {AUTHENTICATION_SERVICE_VENDOR}"
    )
