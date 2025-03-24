import asyncio

import uvicorn

from config import app_config
from internal.app import init_health_check_server, init_http_server
from internal.patterns import Container, initialize_relational_db


async def init_container():
    container = Container()
    await initialize_relational_db(container=container)


http_server_ = init_http_server()


async def main_http_server():
    config = uvicorn.Config(
        app="main:http_server_",
        host="0.0.0.0",
        port=8080,
        log_level=app_config.log_level.lower(),
        workers=app_config.uvicorn_workers,
    )
    server = uvicorn.Server(config)
    await server.serve()


health_check_server_ = init_health_check_server()


async def main_health_check_server():
    config = uvicorn.Config(
        app="main:health_check_server_",
        host="0.0.0.0",
        port=5000,
        log_level=app_config.log_level.lower(),
        workers=app_config.uvicorn_workers,
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(init_container(), main_health_check_server(), main_http_server())
    )
    loop.close()
