from dependency_injector import containers, providers

from config import app_config
from internal.domains.services import AuthenticationSVC, CommentSVC, PostSVC, UserSVC
from internal.domains.usecases import AuthenticationUC, CommentUC, PostUC, UserUC
from internal.infrastructures.external_authentication_service import (
    ExternalAuthenticationServiceClient,
)
from internal.infrastructures.external_rebac_authorization_service import (
    ExternalReBACAuthorizationServiceClient,
)
from internal.infrastructures.relational_db import (
    CommentRepo,
    Database,
    PostRepo,
    UserRepo,
)
from internal.infrastructures.relational_db.base import Base
from internal.infrastructures.relational_db.patterns import AsyncSQLAlchemyUnitOfWork


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            __name__,
            "internal.controllers.http.v1.endpoints.post",
            "internal.controllers.http.v1.endpoints.comment",
            "internal.controllers.http.v1.endpoints.authentication",
            "internal.app.middlewares",
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

    ## External Authentication Service
    external_authentication_svc = providers.Resource(
        ExternalAuthenticationServiceClient,
        url=app_config.authentication_service.url,
        admin_username=app_config.authentication_service.admin_username,
        admin_password=app_config.authentication_service.admin_password,
        realm=app_config.authentication_service.realm,
        client_id=app_config.authentication_service.client_id,
        client_secret=app_config.authentication_service.client_secret,
        webhook_secret=app_config.authentication_service.webhook_secret,
    )

    ## External ReBAC Authorization Service
    external_rebac_authorization_svc = providers.Resource(
        ExternalReBACAuthorizationServiceClient,
        url=app_config.rebac_authorization_service.url,
        api_token=app_config.rebac_authorization_service.token,
        store_id=app_config.rebac_authorization_service.store_id,
        authorization_model_id=app_config.rebac_authorization_service.authorization_model_id,
        timeout_in_millis=app_config.rebac_authorization_service.timeout_in_millis,
    )

    ### Repositories
    post_repo = providers.Factory(PostRepo, session=relational_db_session)
    comment_repo = providers.Factory(CommentRepo, session=relational_db_session)
    user_repo = providers.Factory(UserRepo, session=relational_db_session)

    ### Unit of Work
    relational_db_uow = providers.Factory(
        AsyncSQLAlchemyUnitOfWork,
        session=relational_db_session,
        scoped_session=relational_db_scoped_session,
        post_repo=post_repo,
        comment_repo=comment_repo,
        user_repo=user_repo,
    )

    # Domains
    ## UseCases
    post_uc = providers.Factory(PostUC, relational_db_post_repo=post_repo)
    comment_uc = providers.Factory(CommentUC, relational_db_comment_repo=comment_repo)
    user_uc = providers.Factory(UserUC, relational_db_user_repo=user_repo)
    authentication_uc = providers.Factory(
        AuthenticationUC, external_authentication_svc=external_authentication_svc
    )

    ## Services
    post_svc = providers.Factory(
        PostSVC,
        relational_db_uow=relational_db_uow,
        post_uc=post_uc,
        comment_uc=comment_uc,
        user_uc=user_uc,
    )
    comment_svc = providers.Factory(
        CommentSVC,
        relational_db_uow=relational_db_uow,
        comment_uc=comment_uc,
        user_uc=user_uc,
    )
    user_svc = providers.Factory(
        UserSVC,
        relational_db_uow=relational_db_uow,
        user_uc=user_uc,
        post_uc=post_uc,
        comment_uc=comment_uc,
    )
    authentication_svc = providers.Factory(
        AuthenticationSVC,
        relational_db_uow=relational_db_uow,
        authentication_uc=authentication_uc,
        user_uc=user_uc,
    )


async def initialize_relational_db(container: Container):
    """Initialize the relational database."""
    await container.relational_db().initialize_db(declarative_base=Base)
