import grpc
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from internal.app import JWTAuthMiddleware
from internal.controllers.http.v1.routes import api_router as api_router_v1
from internal.controllers.responses import DataResponse, MessageResponse
from internal.patterns import Container
from utils.logger_utils import GRPCLoggingInterceptor, get_shared_logger

logger = get_shared_logger()


def init_http_server() -> FastAPI:
    server_ = FastAPI(default_response_class=ORJSONResponse)

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


def init_health_check_server(app_status: DataResponse) -> FastAPI:
    health_check_app = FastAPI()

    @health_check_app.get("/health-check")
    async def health_check():
        return ORJSONResponse(
            content=jsonable_encoder(app_status),
            status_code=app_status.message.status_code,
        )

    return health_check_app


def init_grpc_server(container: Container) -> grpc.aio.Server:
    logging_interceptor = GRPCLoggingInterceptor()
    server = grpc.aio.server(interceptors=[logging_interceptor])

    # Instantiate your service
    # TODO: implement a gRPC service

    # Add your service to the gRPC server
    # TODO: add a gRPC service to gRPC server

    logger.info("gRPC server initialized")
    return server
