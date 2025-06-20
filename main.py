import asyncio
from contextlib import asynccontextmanager

import uvicorn

from config import app_config
from config import logger as deferred_logger
from internal.app import init_health_check_server, init_http_server
from internal.controllers.responses import DataResponse
from internal.controllers.responses.error_code import common_internal_error
from internal.controllers.responses.success_code import server_ok
from internal.infrastructures.config_manager import ConfigManager
from internal.patterns import Container, initialize_relational_db
from internal.patterns.dependency_injection import close_relational_db
from utils.logger_utils import get_shared_logger

# Get the configured logger
logger = get_shared_logger()

# Set the real logger for our DeferredLogger in config.py
deferred_logger.set_real_logger(logger)


@asynccontextmanager
async def app_lifespan(app_status: DataResponse):
    """
    Manages the application's lifecycle, including the DI container and database connections.
    """

    # Get the container instance
    container = Container()
    try:
        # Load config from the config manager
        if app_config.cfg_manager_service.enable:
            cfg_manager = ConfigManager(
                address=app_config.cfg_manager_service.url,
                token=app_config.cfg_manager_service.token,
                env=app_config.cfg_manager_service.env,
                app_config=app_config,
                di_container=container,
            )
            await cfg_manager.load()
            await cfg_manager.update_app_config()
            logger.info(f"Load config from server successfully")
        else:
            container.config.from_dict(app_config.model_dump())
            logger.info(f"Load config from local successfully")

        # Wire the container to all necessary modules
        container.wire(
            modules=[
                __name__,
                "internal.controllers.http.v1.endpoints.post",
                "internal.controllers.http.v1.endpoints.comment",
                "internal.controllers.http.v1.endpoints.authentication",
                "internal.app.middlewares",
            ]
        )
        logger.info("Container wiring complete.")

        # Initialize relational database
        await initialize_relational_db(container=container)
        logger.info("Relational database initialized")

        yield container

    except Exception as exc:
        logger.opt(exception=True).error(f"App lifespan crashed unexpectedly: {exc}")
        app_status.message = common_internal_error
    finally:
        # Cleanup resources
        await close_relational_db(container=container)
        logger.info("Relational database closed.")
        container.unwire()
        logger.info("Container unwired.")


async def serve_http(app: uvicorn.Config, app_status: DataResponse):
    server_ = uvicorn.Server(config=app)
    try:
        await server_.serve()
    except Exception as exc:
        logger.opt(exception=True).critical(f"HTTP server crashed unexpectedly: {exc}")
        app_status.message = common_internal_error


async def main():
    """Main entry point for the application."""
    app_status = DataResponse(message=server_ok)

    try:
        async with app_lifespan(app_status=app_status) as container:
            if not container:
                raise RuntimeError(
                    "DI container was not provided by the lifespan manager."
                )

            # --- HTTP Server ---
            http_app = init_http_server()
            http_config = uvicorn.Config(
                app=http_app,
                host="0.0.0.0",
                port=app_config.main_http_port,
                log_level=app_config.log_level.lower(),
                log_config=None,
            )

            # --- Health Check Server ---
            health_app = init_health_check_server(app_status=app_status)
            health_config = uvicorn.Config(
                app=health_app,
                host="0.0.0.0",
                port=app_config.health_check_http_port,
                log_level=app_config.log_level.lower(),
                log_config=None,
            )

            # --- Run all servers concurrently ---
            await asyncio.gather(
                serve_http(app=http_config, app_status=app_status),
                serve_http(app=health_config, app_status=app_status),
            )
    except Exception as exc:
        logger.opt(exception=True).critical(
            f"Application could not start or has crashed due to: {exc}"
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application shut down by user.")
