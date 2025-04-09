from typing import Optional

from dynaconf import Dynaconf
from loguru import logger
from pydantic import BaseModel, Field

# Load settings
settings = Dynaconf(
    envvar_prefix="APP",
    settings_files=["./config/settings.toml", "./config/settings.local.toml"],
    environments=True,
)


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
    log_level: Optional[str] = Field("INFO", alias="LOG_LEVEL")
    uvicorn_workers: Optional[int] = Field(1, alias="UVICORN_WORKERS")
    # Relational DB configs
    relational_db: RelationalDBConfig = Field(..., alias="RELATIONAL_DB")
    # Authentication Service configs
    authentication_service: AuthenticationServiceConfig = Field(
        ..., alias="AUTHENTICATION_SERVICE"
    )


# Load and validate configuration
try:
    app_config = AppConfig(
        ENV_FOR_DYNACONF=settings.ENV_FOR_DYNACONF,
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
    )
    logger.info("Configuration loaded successfully!")
except Exception as exc:
    logger.error(f"Configuration validation error: {exc}")
