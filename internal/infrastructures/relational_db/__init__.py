from enum import Enum

from config import app_config

from .abstraction import AbstractCommentRepo, AbstractPostRepo
from .base import Base

# from .patterns import RelationalDBContainer
from .postgres import PostgresDatabase


class SupportedDatabaseVendor(str, Enum):
    POSTGRES = "postgres"


DATABASE_VENDOR = app_config.relational_db.vendor

if DATABASE_VENDOR == SupportedDatabaseVendor.POSTGRES.value:
    from internal.infrastructures.relational_db.postgres import (
        PostgresDatabase as Database,
    )

    # repositories
    from internal.infrastructures.relational_db.postgres.repositories import (
        CommentRepo,
        PostRepo,
    )
else:
    raise RuntimeError(f"Invalid database vendor {DATABASE_VENDOR}")
