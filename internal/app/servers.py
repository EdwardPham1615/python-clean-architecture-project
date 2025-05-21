from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from config import app_config
from internal.app import JWTAuthMiddleware
from internal.controllers.http.v1.routes import api_router as api_router_v1
from internal.controllers.responses import DataResponse, MessageResponse
from internal.infrastructures.config_manager import ConfigManager
from internal.patterns import Container, initialize_relational_db
from internal.patterns.dependency_injection import close_relational_db
from utils.logger_utils import get_shared_logger

logger = get_shared_logger()

app_status = {"alive": True, "status_code": 200, "message": "I'm fine"}


def init_http_server() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            # Get the container instance
            container = Container()

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

            # Initialize relational database
            await initialize_relational_db(container=container)
            logger.info("Relational database initialized")

            yield

            # Close relational database
            await close_relational_db(container=container)
            logger.info("Relational database closed")
        except Exception as exc:
            logger.error(f"Main HTTP server crashed due to: {exc}")
            app_status["alive"] = False
            app_status["status_code"] = 500
            app_status["message"] = str(exc)

    server_ = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)

    server_.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    server_.add_middleware(
        middleware_class=JWTAuthMiddleware,
        excluded_paths=[
            "/redoc",  # Redoc
            "/docs",  # OpenAPI docs
            "/openapi.json",  # OpenAPI spec
            "/v1/authentication/webhook/events-synchronization",  # webhook to integrate with authentication service
        ],
    )

    @server_.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        logger.error(exc)
        res = DataResponse(
            message=MessageResponse(
                msg_code="E000", msg_name=str(exc.detail), status_code=exc.status_code
            )
        )
        return ORJSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(res),
        )

    server_.include_router(api_router_v1, prefix="/v1")

    return server_


def init_health_check_server() -> FastAPI:
    health_check_app = FastAPI()

    @health_check_app.get("/health-check")
    async def health_check():
        if app_status["status_code"] != 200:
            logger.info(app_status)
        return ORJSONResponse(content=app_status, status_code=app_status["status_code"])

    return health_check_app
