from dependency_injector import containers, providers

from internal.domains.services import AuthenticationSVC, CommentSVC, PostSVC, UserSVC
from internal.domains.usecases import (
    AuthenticationUC,
    AuthorizationUC,
    CommentUC,
    PostUC,
    UserUC,
)
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

    config = providers.Configuration()

    # Infrastructures
    ## Relational DB
    relational_db = providers.Resource(
        Database,
        db_url=config.relational_db.url,
        enable_log=config.relational_db.enable_log,
        enable_migrations=config.relational_db.enable_auto_migrate,
    )

    relational_db_scoped_session = providers.Resource(
        relational_db.provided.scoped_session, relational_db
    )

    ## External Authentication Service
    external_authentication_svc = providers.Resource(
        ExternalAuthenticationServiceClient,
        url=config.authentication_service.url,
        admin_username=config.authentication_service.admin_username,
        admin_password=config.authentication_service.admin_password,
        realm=config.authentication_service.realm,
        client_id=config.authentication_service.client_id,
        client_secret=config.authentication_service.client_secret,
        webhook_secret=config.authentication_service.webhook_secret,
    )

    ## External ReBAC Authorization Service
    external_rebac_authorization_svc = providers.Resource(
        ExternalReBACAuthorizationServiceClient,
        url=config.rebac_authorization_service.url,
        api_token=config.rebac_authorization_service.token,
        store_id=config.rebac_authorization_service.store_id,
        authorization_model_id=config.rebac_authorization_service.authorization_model_id,
        timeout_in_millis=config.rebac_authorization_service.timeout_in_millis,
    )

    ### Repositories
    post_repo_factory = providers.Factory(PostRepo)
    comment_repo_factory = providers.Factory(CommentRepo)
    user_repo_factory = providers.Factory(UserRepo)

    ### Unit of Work
    relational_db_uow = providers.Factory(
        AsyncSQLAlchemyUnitOfWork,
        scoped_session=relational_db_scoped_session,
        post_repo_factory=post_repo_factory.provider,
        comment_repo_factory=comment_repo_factory.provider,
        user_repo_factory=user_repo_factory.provider,
    )

    # Domains
    ## UseCases
    post_uc = providers.Factory(PostUC)
    comment_uc = providers.Factory(CommentUC)
    user_uc = providers.Factory(UserUC)
    authentication_uc = providers.Factory(
        AuthenticationUC, external_authentication_svc=external_authentication_svc
    )
    authorization_uc = providers.Factory(
        AuthorizationUC, external_authorization_svc=external_rebac_authorization_svc
    )

    ## Services
    post_svc = providers.Factory(
        PostSVC,
        relational_db_uow=relational_db_uow,
        post_uc=post_uc,
        comment_uc=comment_uc,
        user_uc=user_uc,
        authorization_uc=authorization_uc,
    )
    comment_svc = providers.Factory(
        CommentSVC,
        relational_db_uow=relational_db_uow,
        comment_uc=comment_uc,
        user_uc=user_uc,
        authorization_uc=authorization_uc,
    )
    user_svc = providers.Factory(
        UserSVC,
        relational_db_uow=relational_db_uow,
        user_uc=user_uc,
        post_uc=post_uc,
        comment_uc=comment_uc,
        authorization_uc=authorization_uc,
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


async def close_relational_db(container: Container):
    """Initialize the relational database."""
    await container.relational_db().close()
