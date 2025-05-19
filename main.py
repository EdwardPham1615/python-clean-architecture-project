import asyncio

import uvicorn

from config import app_config
from config import logger as deferred_logger
from internal.app import init_health_check_server, init_http_server
from utils.logger_utils import get_shared_logger

# Get the configured logger
logger = get_shared_logger()

# Set the real logger for our DeferredLogger in config.py
deferred_logger.set_real_logger(logger)


http_server_ = init_http_server()


async def main_http_server():
    config = uvicorn.Config(
        app="main:http_server_",
        host="0.0.0.0",
        port=app_config.main_http_port,
        log_level=app_config.log_level.lower(),
        log_config=None,  # Disable Uvicorn's logging configuration
        workers=app_config.uvicorn_workers,
    )
    server = uvicorn.Server(config)
    await server.serve()


health_check_server_ = init_health_check_server()


async def main_health_check_server():
    config = uvicorn.Config(
        app="main:health_check_server_",
        host="0.0.0.0",
        port=app_config.health_check_http_port,
        log_level=app_config.log_level.lower(),
        log_config=None,  # Disable Uvicorn's logging configuration
        workers=app_config.uvicorn_workers,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    """Main entry point for the application."""
    await asyncio.gather(main_health_check_server(), main_http_server())


if __name__ == "__main__":
    asyncio.run(main())
