from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class ReBACAuthorizationServiceConfig(BaseModel):
    vendor: Optional[str] = Field("openfga")
    url: str
    token: str
    store_id: str
    authorization_model_id: str
    timeout_in_millis: Optional[int] = 3000


class AuthenticationServiceConfig(BaseModel):
    vendor: Optional[str] = Field("keycloak")
    url: str
    admin_username: str
    admin_password: str
    realm: str
    client_id: str
    client_secret: str
    webhook_secret: str


class RelationalDBConfig(BaseModel):
    vendor: Optional[str] = Field("postgres")
    url: str
    enable_log: bool
    enable_auto_migrate: bool


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./config/.env",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # === General App Settings ===
    main_http_port: Optional[int] = 8080
    health_check_http_port: Optional[int] = 5000
    log_level: Optional[str] = "INFO"
    uvicorn_workers: Optional[int] = 1

    # === Relational DB ===
    relational_db: RelationalDBConfig

    # === Authentication Service ===
    authentication_service: AuthenticationServiceConfig

    # === ReBAC Authorization Service ===
    rebac_authorization_service: ReBACAuthorizationServiceConfig


# Load and validate configuration
try:
    app_config = AppConfig()
    logger.info("Configuration loaded successfully!")
except Exception as exc:
    logger.error(f"Configuration validation error: {exc}")
