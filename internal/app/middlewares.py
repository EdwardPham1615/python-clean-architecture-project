from dependency_injector.wiring import Provide, inject
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from jwcrypto.jws import InvalidJWSObject
from jwcrypto.jwt import JWTExpired
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from internal.controllers.responses import DataResponse
from internal.controllers.responses.error_code import (
    common_invalid_token_error,
    common_missing_or_invalid_token_error,
    common_token_expired_error,
)
from internal.infrastructures.authentication_service.abstraction import (
    AbstractAuthenticationService,
)
from internal.patterns import Container


class JWTAuthMiddleware(BaseHTTPMiddleware):
    @inject
    async def dispatch(
        self,
        request: Request,
        call_next,
        authentication_svc: AbstractAuthenticationService = Provide[
            Container.authentication_svc
        ],
    ):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            res = DataResponse(message=common_missing_or_invalid_token_error)
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, content=jsonable_encoder(res)
            )

        token = auth_header.split(" ")[1]  # Extract token
        try:
            payload = await authentication_svc.decode_token(token=token)
            request.state.user = payload  # Store user info in request state
        except JWTExpired:
            res = DataResponse(message=common_token_expired_error)
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, content=jsonable_encoder(res)
            )
        except InvalidJWSObject:
            res = DataResponse(message=common_invalid_token_error)
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, content=jsonable_encoder(res)
            )

        return await call_next(request)
