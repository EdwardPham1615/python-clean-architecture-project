from typing import Optional

from dynaconf import Dynaconf
from pydantic import BaseModel, Field


# We'll use a deferred logger to avoid circular imports
# This will be replaced with the actual logger once it's available
class DeferredLogger:
    def __init__(self):
        self.messages = []
        self.real_logger = None

    def _log(self, level, message, *args, **kwargs):
        if self.real_logger:
            getattr(self.real_logger, level)(message, *args, **kwargs)
        else:
            self.messages.append((level, message, args, kwargs))

    def info(self, message, *args, **kwargs):
        self._log("info", message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log("warning", message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log("error", message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        self._log("exception", message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self._log("debug", message, *args, **kwargs)

    def set_real_logger(self, _logger):
        self.real_logger = _logger
        # Replay any deferred messages
        for level, message, args, kwargs in self.messages:
            getattr(self.real_logger, level)(message, *args, **kwargs)
        self.messages = []


# Create a deferred logger
logger = DeferredLogger()

# Load settings
settings = Dynaconf(
    envvar_prefix="APP",
    settings_files=["./config/settings.toml", "./config/settings.local.toml"],
    environments=True,
)


class ReBACAuthorizationServiceConfig(BaseModel):
    vendor: Optional[str] = Field("openfga", alias="VENDOR")
    url: str = Field(..., alias="URL")
    token: str = Field(..., alias="TOKEN")
    store_id: str = Field(..., alias="STORE_ID")
    authorization_model_id: str = Field(..., alias="AUTHORIZATION_MODEL_ID")
    timeout_in_millis: Optional[int] = Field(3000, alias="TIMEOUT_IN_MILLIS")


class AuthenticationServiceConfig(BaseModel):
    vendor: Optional[str] = Field("keycloak", alias="VENDOR")
    url: str = Field(..., alias="URL")
    admin_username: str = Field(..., alias="ADMIN_USERNAME")
    admin_password: str = Field(..., alias="ADMIN_PASSWORD")
    realm: str = Field(..., alias="REALM")
    client_id: str = Field(..., alias="CLIENT_ID")
    client_secret: str = Field(..., alias="CLIENT_SECRET")
    webhook_secret: str = Field(..., alias="WEBHOOK_SECRET")


class RelationalDBConfig(BaseModel):
    vendor: Optional[str] = Field("postgres", alias="VENDOR")
    url: str = Field(..., alias="URL")
    enable_auto_migrate: bool = Field(..., alias="ENABLE_AUTO_MIGRATE")


class AppConfig(BaseModel):
    env_for_dynaconf: Optional[str] = Field("development", alias="ENV_FOR_DYNACONF")
    main_http_port: Optional[int] = Field(8080, alias="MAIN_HTTP_PORT")
    health_check_http_port: Optional[int] = Field(5000, alias="HEALTH_CHECK_HTTP_PORT")
    log_level: Optional[str] = Field("INFO", alias="LOG_LEVEL")
    uvicorn_workers: Optional[int] = Field(1, alias="UVICORN_WORKERS")
    # Relational DB configs
    relational_db: RelationalDBConfig = Field(..., alias="RELATIONAL_DB")
    # Authentication Service configs
    authentication_service: AuthenticationServiceConfig = Field(
        ..., alias="AUTHENTICATION_SERVICE"
    )
    # ReBAC Authorization Service configs
    rebac_authorization_service: ReBACAuthorizationServiceConfig = Field(
        ..., alias="REBAC_AUTHORIZATION_SERVICE"
    )


# Load and validate configuration
try:
    app_config = AppConfig(
        ENV_FOR_DYNACONF=settings.ENV_FOR_DYNACONF,
        MAIN_HTTP_PORT=settings.MAIN_HTTP_PORT,
        HEALTH_CHECK_HTTP_PORT=settings.HEALTH_CHECK_HTTP_PORT,
        LOG_LEVEL=settings.LOG_LEVEL,
        UVICORN_WORKERS=settings.UVICORN_WORKERS,
        RELATIONAL_DB=RelationalDBConfig(
            VENDOR=settings.RELATIONAL_DB.VENDOR,
            URL=settings.RELATIONAL_DB.URL,
            ENABLE_AUTO_MIGRATE=settings.RELATIONAL_DB.ENABLE_AUTO_MIGRATE,
        ),
        AUTHENTICATION_SERVICE=AuthenticationServiceConfig(
            VENDOR=settings.AUTHENTICATION_SERVICE.VENDOR,
            URL=settings.AUTHENTICATION_SERVICE.URL,
            ADMIN_USERNAME=settings.AUTHENTICATION_SERVICE.ADMIN_USERNAME,
            ADMIN_PASSWORD=settings.AUTHENTICATION_SERVICE.ADMIN_PASSWORD,
            REALM=settings.AUTHENTICATION_SERVICE.REALM,
            CLIENT_ID=settings.AUTHENTICATION_SERVICE.CLIENT_ID,
            CLIENT_SECRET=settings.AUTHENTICATION_SERVICE.CLIENT_SECRET,
            WEBHOOK_SECRET=settings.AUTHENTICATION_SERVICE.WEBHOOK_SECRET,
        ),
        REBAC_AUTHORIZATION_SERVICE=ReBACAuthorizationServiceConfig(
            VENDOR=settings.REBAC_AUTHORIZATION_SERVICE.VENDOR,
            URL=settings.REBAC_AUTHORIZATION_SERVICE.URL,
            TOKEN=settings.REBAC_AUTHORIZATION_SERVICE.TOKEN,
            STORE_ID=settings.REBAC_AUTHORIZATION_SERVICE.STORE_ID,
            AUTHORIZATION_MODEL_ID=settings.REBAC_AUTHORIZATION_SERVICE.AUTHORIZATION_MODEL_ID,
            TIMEOUT_IN_MILLIS=settings.REBAC_AUTHORIZATION_SERVICE.TIMEOUT_IN_MILLIS,
        ),
    )
    logger.info("Configuration loaded successfully!")
except Exception as exc:
    logger.error(f"Configuration validation error: {exc}")
