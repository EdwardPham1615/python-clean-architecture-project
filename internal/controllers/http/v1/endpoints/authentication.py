from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

from internal.controllers.responses import DataResponse
from internal.controllers.responses.error_code import (
    common_internal_error,
    invalid_webhook_secret_error,
    sync_webhook_event_fail,
)
from internal.controllers.responses.success_code import sync_webhook_event_success
from internal.domains.errors import UnauthorizedWebhookException
from internal.domains.services import AuthenticationSVC
from internal.patterns import Container
from utils.logger_utils import get_shared_logger

logger = get_shared_logger()

router = APIRouter()


@router.post("/webhook/events-synchronization", response_model=DataResponse)
@inject
async def sync_event_webhook(
    ctx_req_: Request,
    svc: Annotated[AuthenticationSVC, Depends(Provide[Container.authentication_svc])],
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        error_ = await svc.handle_webhook_event(ctx_req_=ctx_req_)
        if error_:
            if isinstance(error_, UnauthorizedWebhookException):
                res = DataResponse(message=invalid_webhook_secret_error)
            else:
                res = DataResponse(message=sync_webhook_event_fail)
        else:
            res = DataResponse(message=sync_webhook_event_success)
    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )
