from enum import Enum

from config import app_config


class SupportedReBACAuthorizationService(str, Enum):
    OPENFGA = "openfga"


REBAC_AUTHORIZATION_SERVICE_VENDOR = app_config.rebac_authorization_service.vendor

if REBAC_AUTHORIZATION_SERVICE_VENDOR == SupportedReBACAuthorizationService.OPENFGA:
    from internal.infrastructures.external_rebac_authorization_service.openfga_client import (
        OpenFGAClient as ExternalReBACAuthorizationServiceClient,
    )
else:
    raise RuntimeError(
        f"Invalid rebac authorization service vendor {REBAC_AUTHORIZATION_SERVICE_VENDOR}"
    )
