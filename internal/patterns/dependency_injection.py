from dependency_injector import containers, providers

from internal.domains.services import PostSVC, CommentSVC
from internal.domains.usecases import PostUC, CommentUC
from internal.infrastructures.relational_db.patterns import AsyncSQLAlchemyUnitOfWork
from internal.infrastructures.relational_db.base import Base
from internal.infrastructures.relational_db import Database, PostRepo, CommentRepo
from config import app_config


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            __name__,
            "internal.controllers.http.v1.endpoints.post",
            "internal.controllers.http.v1.endpoints.comment",
        ]
    )

    # Infrastructures
    ## Relational DB
    relational_db = providers.Resource(
        Database,
        db_url=app_config.relational_db.url,
        enable_migrations=app_config.relational_db.enable_auto_migrate,
    )

    async def get_relational_db_session(relational_db_: Database):
        async with relational_db_.session() as session:  # Enters the context
            yield session  # Returns an AsyncSession instance

    relational_db_session = providers.Resource(get_relational_db_session, relational_db)
    relational_db_scoped_session = providers.Resource(
        relational_db.provided.scoped_session, relational_db
    )

    ### Repositories
    post_repo = providers.Factory(PostRepo, session=relational_db_session)
    comment_repo = providers.Factory(CommentRepo, session=relational_db_session)

    ### Unit of Work
    relational_db_uow = providers.Factory(
        AsyncSQLAlchemyUnitOfWork,
        session=relational_db_session,
        scoped_session=relational_db_scoped_session,
        post_repo=post_repo,
        comment_repo=comment_repo,
    )

    # Domains
    ## UseCases
    post_uc = providers.Factory(PostUC, relational_db_post_repo=post_repo)
    comment_uc = providers.Factory(CommentUC, relational_db_comment_repo=comment_repo)

    ## Services
    post_svc = providers.Factory(
        PostSVC,
        relational_db_uow=relational_db_uow,
        post_uc=post_uc,
        comment_uc=comment_uc,
    )
    comment_svc = providers.Factory(
        CommentSVC, relational_db_uow=relational_db_uow, comment_uc=comment_uc
    )


async def initialize_relational_db(container: Container):
    """Initialize the relational database."""
    await container.relational_db().initialize_db(declarative_base=Base)
