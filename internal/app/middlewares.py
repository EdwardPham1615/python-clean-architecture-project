from dependency_injector.wiring import Provide, inject
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from jwcrypto.jws import InvalidJWSObject
from jwcrypto.jwt import JWTExpired
from loguru import logger
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from internal.controllers.responses import DataResponse
from internal.controllers.responses.error_code import (
    common_invalid_token_error,
    common_missing_or_invalid_token_error,
    common_token_expired_error,
)
from internal.domains.entities import JWTPayload
from internal.domains.services.abstraction import AbstractAuthenticationSVC
from internal.patterns import Container


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths: list[str] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or []

    @inject
    async def dispatch(
        self,
        request: Request,
        call_next,
        authentication_svc: AbstractAuthenticationSVC = Provide[
            Container.authentication_svc
        ],
    ):
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            res = DataResponse(message=common_missing_or_invalid_token_error)
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, content=jsonable_encoder(res)
            )

        token = auth_header.split(" ")[1]  # Extract token
        try:
            (raw_payload, error) = await authentication_svc.decode_token(token=token)
            if error:
                res = DataResponse(message=common_missing_or_invalid_token_error)
                return ORJSONResponse(
                    status_code=common_missing_or_invalid_token_error.status_code,
                    content=jsonable_encoder(res),
                )
            try:
                payload = JWTPayload(**raw_payload)
            except Exception as exc:
                logger.error(exc)
                res = DataResponse(message=common_invalid_token_error)
                return ORJSONResponse(
                    status_code=common_invalid_token_error.status_code,
                    content=jsonable_encoder(res),
                )
            user_id = payload.sub
            if not user_id:
                res = DataResponse(message=common_invalid_token_error)
                return ORJSONResponse(
                    status_code=common_invalid_token_error.status_code,
                    content=jsonable_encoder(res),
                )
            request.state.user_id = user_id  # Store user id in request state
        except JWTExpired:
            res = DataResponse(message=common_token_expired_error)
            return ORJSONResponse(
                status_code=common_token_expired_error.status_code,
                content=jsonable_encoder(res),
            )
        except InvalidJWSObject:
            res = DataResponse(message=common_invalid_token_error)
            return ORJSONResponse(
                status_code=common_invalid_token_error.status_code,
                content=jsonable_encoder(res),
            )

        return await call_next(request)
