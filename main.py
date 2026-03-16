import asyncio
import signal
from contextlib import asynccontextmanager

import grpc
import uvicorn

from config import app_config
from config import logger as deferred_logger
from internal.app import init_grpc_server, init_http_server
from internal.controllers.responses import DataResponse, HealthState
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

    container = Container()
    container_wired = False
    db_initialized = False
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
            load_err = await cfg_manager.load()
            if load_err is not None:
                raise RuntimeError(
                    "Failed to load config from config manager"
                ) from load_err
            await cfg_manager.update_app_config()
            logger.info("Load config from server successfully")
        else:
            container.config.from_dict(app_config.model_dump())
            logger.info("Load config from local successfully")

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
        container_wired = True
        logger.info("Container wiring complete.")

        # Initialize relational database
        await initialize_relational_db(container=container)
        db_initialized = True
        logger.info("Relational database initialized")

        yield container

    except Exception as exc:
        logger.opt(exception=True).error(f"App lifespan crashed unexpectedly: {exc}")
        app_status.message = common_internal_error
        raise
    finally:
        # Cleanup resources
        if db_initialized:
            try:
                await close_relational_db(container=container)
                logger.info("Relational database closed.")
            except Exception as exc:
                logger.opt(exception=True).warning(
                    f"Relational database close failed: {exc}"
                )
        if container_wired:
            container.unwire()
            logger.info("Container unwired.")


async def cancel_and_wait(task: asyncio.Task | None, server_name: str) -> None:
    if task is None:
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        logger.opt(exception=True).warning(f"{server_name} task cleanup failed: {exc}")


async def serve_http(
    app: uvicorn.Config,
    health_state: HealthState,
    stop_event: asyncio.Event,
    server_name: str,
    report_ready: bool,
):
    server_ = uvicorn.Server(config=app)
    server_task: asyncio.Task | None = None
    stop_task: asyncio.Task | None = None
    pending_error: BaseException | None = None

    try:
        server_task = asyncio.create_task(server_.serve())
        stop_task = asyncio.create_task(stop_event.wait())

        while not server_.started and not server_task.done():
            if stop_event.is_set():
                server_.should_exit = True
                break
            await asyncio.sleep(0.05)

        if server_.started:
            logger.info(f"{server_name} started")
            if report_ready:
                health_state.set_http_ready(True)
        elif stop_event.is_set():
            logger.info(f"{server_name} startup interrupted by shutdown signal")
        else:
            task_exc = server_task.exception()
            if task_exc is not None:
                raise RuntimeError(f"{server_name} failed to start") from task_exc
            raise RuntimeError(f"{server_name} failed to start")

        done, _ = await asyncio.wait(
            {server_task, stop_task},
            return_when=asyncio.FIRST_COMPLETED,
        )

        if stop_task in done:
            logger.info(f"{server_name} received shutdown signal")
            server_.should_exit = True
            await server_task
        else:
            if stop_event.is_set():
                logger.info(f"{server_name} stopped after shutdown signal")
            else:
                task_exc = server_task.exception()
                if task_exc is not None:
                    raise RuntimeError(
                        f"{server_name} stopped unexpectedly"
                    ) from task_exc
                raise RuntimeError(f"{server_name} stopped unexpectedly")
    except asyncio.CancelledError as exc:
        pending_error = exc
        server_.should_exit = True
        logger.info(f"{server_name} task cancelled")
    except Exception as exc:
        logger.opt(exception=True).critical(
            f"{server_name} crashed unexpectedly: {exc}"
        )
        health_state.mark_error(message=common_internal_error)
        stop_event.set()
        pending_error = exc
    finally:
        await cancel_and_wait(stop_task, server_name)

        if server_task is not None:
            if not server_task.done():
                server_.should_exit = True
            server_result = (await asyncio.gather(server_task, return_exceptions=True))[
                0
            ]
            if isinstance(server_result, BaseException) and not isinstance(
                server_result, asyncio.CancelledError
            ):
                if pending_error is None:
                    pending_error = server_result
                logger.opt(exception=True).warning(
                    f"{server_name} did not stop cleanly: {server_result}"
                )

        if report_ready:
            health_state.set_http_ready(False)

    if pending_error is not None:
        raise pending_error


async def serve_grpc(
    server: grpc.aio.Server,
    health_state: HealthState,
    stop_event: asyncio.Event,
    server_name: str,
    report_ready: bool,
):
    stop_task: asyncio.Task | None = None
    termination_task: asyncio.Task | None = None
    started = False
    pending_error: BaseException | None = None

    try:
        listen_addr = f"0.0.0.0:{app_config.main_grpc_port}"
        bound_port = server.add_insecure_port(listen_addr)
        if bound_port == 0:
            raise RuntimeError(f"{server_name} failed to bind on {listen_addr}")

        logger.info(f"{server_name} starting on {listen_addr}")

        await server.start()
        started = True
        logger.info(f"{server_name} started")

        if report_ready:
            health_state.set_grpc_ready(True)

        termination_task = asyncio.create_task(server.wait_for_termination())
        stop_task = asyncio.create_task(stop_event.wait())

        done, _ = await asyncio.wait(
            {termination_task, stop_task},
            return_when=asyncio.FIRST_COMPLETED,
        )

        if stop_task in done:
            logger.info(f"{server_name} received shutdown signal")
        else:
            raise RuntimeError(f"{server_name} stopped unexpectedly")
    except asyncio.CancelledError as exc:
        pending_error = exc
        logger.info(f"{server_name} task cancelled")
    except Exception as exc:
        logger.opt(exception=True).critical(
            f"{server_name} crashed unexpectedly: {exc}"
        )
        health_state.mark_error(message=common_internal_error)
        stop_event.set()
        pending_error = exc
    finally:
        logger.info(f"Shutting down {server_name}")

        await cancel_and_wait(stop_task, server_name)
        await cancel_and_wait(termination_task, server_name)

        if started:
            try:
                await server.stop(grace=1)
            except Exception as exc:
                logger.opt(exception=True).warning(
                    f"{server_name} did not stop cleanly: {exc}"
                )

        if report_ready:
            health_state.set_grpc_ready(False)

        logger.info(f"{server_name} shut down")

    if pending_error is not None:
        raise pending_error


def install_signal_handlers(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()

    def _handle_signal(sig: signal.Signals) -> None:
        logger.info(f"Received {sig.name}, shutting down.")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _handle_signal, sig)
        except NotImplementedError:
            logger.warning("Signal handlers are not supported on this platform.")
            break
        except RuntimeError:
            logger.warning("Signal handlers must be installed in the main thread.")
            break


async def main():
    """Main entry point for the application."""
    app_status = DataResponse(message=server_ok)
    stop_event = asyncio.Event()
    install_signal_handlers(stop_event)

    try:
        async with app_lifespan(app_status=app_status) as container:
            if not container:
                raise RuntimeError(
                    "DI container was not provided by the lifespan manager."
                )

            health_state = HealthState(app_status=app_status)
            health_state.refresh()

            # --- HTTP Server ---
            http_app = init_http_server(app_status=app_status)
            http_config = uvicorn.Config(
                app=http_app,
                host="0.0.0.0",
                port=app_config.main_http_port,
                log_level=app_config.log_level.lower(),
                log_config=None,
                loop="uvloop",
            )

            # --- gRPC Server ---
            # Get the gRPC service with all dependencies injected from the container
            grpc_server_instance = init_grpc_server(container=container)

            # --- Run all servers concurrently ---
            async with asyncio.TaskGroup() as tg:
                tg.create_task(
                    serve_http(
                        app=http_config,
                        health_state=health_state,
                        stop_event=stop_event,
                        server_name="Main HTTP server",
                        report_ready=True,
                    )
                )

                tg.create_task(
                    serve_grpc(
                        server=grpc_server_instance,
                        health_state=health_state,
                        stop_event=stop_event,
                        server_name="gRPC server",
                        report_ready=True,
                    )
                )

                await stop_event.wait()

    except Exception as exc:
        logger.opt(exception=True).critical(
            f"Application could not start or has crashed due to: {exc}"
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application shut down by user.")
