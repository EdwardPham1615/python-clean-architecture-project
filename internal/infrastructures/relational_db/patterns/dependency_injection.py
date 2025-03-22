# """
# Dependency Injection Configuration using `python-dependency-injector`.
#
# This module sets up dependency injection for database interactions within
# the application, utilizing `python-dependency-injector`. It supports relational
# databases and can be extended for other types of infrastructures.
#
# Usage:
#     from internal.infrastructures.relational_db.patterns.dependency_injection import relational_db_container
#
#     async with relational_db_container.unit_of_work() as uow:
#         await uow.post_repo.create_post(...)
# """
#
# from dependency_injector import containers, providers
# from internal.infrastructures.relational_db.patterns import AsyncSQLAlchemyUnitOfWork
# from internal.infrastructures.relational_db.base import Base
# from enum import Enum
# from config import app_config
#
#
# class SupportedDatabaseVendor(str, Enum):
#     POSTGRES = "postgres"
#
#
# DATABASE_VENDOR = app_config.relational_db.vendor
#
#
# if DATABASE_VENDOR == SupportedDatabaseVendor.POSTGRES.value:
#     from internal.infrastructures.relational_db.postgres import (
#         PostgresDatabase as Database,
#     )
#
#     # repositories
#     from internal.infrastructures.relational_db.postgres.repositories import PostRepo
#     from internal.infrastructures.relational_db.postgres.repositories import CommentRepo
# else:
#     raise RuntimeError(f"Invalid database vendor {DATABASE_VENDOR}")
#
#
# class RelationalDBContainer(containers.DeclarativeContainer):
#     """Dependency injection container for relational database components."""
#
#     wiring_config = containers.WiringConfiguration(modules=[__name__])
#
#     # Relational DB
#     db = providers.Singleton(
#         Database,
#         db_url=app_config.relational_db.url,
#         enable_migrations=app_config.relational_db.enable_auto_migrate,
#     )
#
#     # Repositories
#     post_repo = providers.Factory(PostRepo, session=db.provided.session_scope)
#     comment_repo = providers.Factory(CommentRepo, session=db.provided.session_scope)
#
#     # Unit of Work
#     unit_of_work = providers.Factory(
#         AsyncSQLAlchemyUnitOfWork,
#         session=db.provided.session_scope,
#         scoped_session=db.provided.session,
#         post_repo=post_repo,
#         comment_repo=comment_repo,
#     )
#
#     async def initialize_db(self):
#         await self.db().initialize_db(declarative_base=Base)
