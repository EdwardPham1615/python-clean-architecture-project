from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from internal.controllers.http.v1.routes import api_router as api_router_v1
from internal.controllers.responses import DataResponse, MessageResponse

app_status = {"alive": True, "status_code": 200, "message": "I'm fine"}


def init_http_server() -> FastAPI:
    # @asynccontextmanager
    # async def lifespan(app: FastAPI):
    #     # startup
    #
    #     yield
    #
    #     # shutdown
    #     logger.info("Shutting down")
    #     app_status["alive"] = False
    #     app_status["status_code"] = 500
    #     app_status["message"] = "Shut down"

    server_ = FastAPI(default_response_class=ORJSONResponse)

    server_.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
