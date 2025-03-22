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


# Load and validate configuration
try:
    app_config = AppConfig(**settings.as_dict())
    logger.info("Configuration loaded successfully!")
except Exception as exc:
    logger.error(f"Configuration validation error: {exc}")
