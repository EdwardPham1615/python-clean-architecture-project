from typing import Annotated, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from loguru import logger
from pydantic import UUID4, Field, ValidationError

from internal.controllers.http.payloads import (
    CreateCommentRequestV1,
    UpdateCommentRequestV1,
)
from internal.controllers.http.resources import (
    CreateCommentResourceV1,
    GetCommentResourceV1,
)
from internal.controllers.responses import DataResponse
from internal.controllers.responses.error_code import (
    common_internal_error,
    common_no_permission_error,
    common_validation_error,
    create_comment_fail,
    delete_comment_fail,
    get_comment_fail,
    update_comment_fail,
)
from internal.controllers.responses.success_code import (
    create_comment_success,
    delete_comment_success,
    get_comment_success,
    update_comment_success,
)
from internal.domains.entities import DeleteCommentPayload, GetMultiCommentsFilter
from internal.domains.errors import (
    CreateCommentException,
    DeleteCommentException,
    GetCommentException,
    UnauthorizeException,
    UpdateCommentException,
)
from internal.domains.services import CommentSVC
from internal.patterns import Container

router = APIRouter()


@router.post("", response_model=DataResponse)
@inject
async def create(
    ctx_req_: Request,
    req_: CreateCommentRequestV1,
    svc: Annotated[CommentSVC, Depends(Provide[Container.comment_svc])],
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        # get user id from context request
        user_id = ctx_req_.state.user_id

        # validate request body
        try:
            req_.validate_()
        except ValidationError as exc:
            logger.error(exc)
            res = DataResponse(message=common_validation_error)
            return ORJSONResponse(
                status_code=common_validation_error.status_code,
                content=jsonable_encoder(res),
            )

        # convert request body to payload
        payload = req_.to_payload()
        payload.owner_id = str(user_id)

        # execute
        (new_comment, error_) = await svc.create(payload=payload)
        if error_:
            if isinstance(error_, CreateCommentException):
                res = DataResponse(message=create_comment_fail)
        else:
            resource = CreateCommentResourceV1()
            resource.from_entity(entity=new_comment)
            res = DataResponse(data=[resource], count=1, message=create_comment_success)

    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )


@router.get("/{comment_id}", response_model=DataResponse)
@inject
async def get_by_id(
    comment_id: str, svc: Annotated[CommentSVC, Depends(Provide[Container.comment_svc])]
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        # validate request body
        try:
            UUID4(comment_id)
        except Exception as exc:
            logger.error(exc)
            res = DataResponse(message=common_validation_error)
            return ORJSONResponse(
                status_code=common_validation_error.status_code,
                content=jsonable_encoder(res),
            )

        # execute
        (comment_, error_) = await svc.get_by_id(id_=comment_id)
        if error_:
            if isinstance(error_, GetCommentException):
                res = DataResponse(message=get_comment_fail)
        else:
            resource = GetCommentResourceV1()
            resource.from_entity(entity=comment_)
            res = DataResponse(data=[resource], count=1, message=get_comment_success)

    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )


@router.get("", response_model=DataResponse)
@inject
async def get_multi(
    svc: Annotated[CommentSVC, Depends(Provide[Container.comment_svc])],
    sort_field: Annotated[
        str, Field(description="Enum: updated_at, created_at")
    ] = "updated_at",
    sort_order: Annotated[str, Field(description="Enum: DESC, ASC")] = "DESC",
    offset: int = 0,
    limit: int = 100,
    from_date: Optional[
        Annotated[str, Field(description="yyyy-mm-ddThh:mm:ss.ffffff")]
    ] = None,
    to_date: Optional[
        Annotated[str, Field(description="yyyy-mm-ddThh:mm:ss.ffffff")]
    ] = None,
    post_id: Optional[str] = None,
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        # validate request body
        try:
            filter_ = GetMultiCommentsFilter(
                sort_field=sort_field,
                sort_order=sort_order,
                offset=offset,
                limit=limit,
                from_date=from_date,
                to_date=to_date,
                post_id=post_id,
                enable_count=True,
            )
            filter_.validate_()
        except ValidationError as exc:
            logger.error(exc)
            res = DataResponse(message=common_validation_error)
            return ORJSONResponse(
                status_code=common_validation_error.status_code,
                content=jsonable_encoder(res),
            )

        # execute
        ((comments_, count), error_) = await svc.get_multi(filter_=filter_)
        if error_:
            if isinstance(error_, GetCommentException):
                res = DataResponse(message=get_comment_fail)
        else:
            resource = GetCommentResourceV1()
            resources = [
                resource.from_entity(entity=comment_) for comment_ in comments_
            ]
            res = DataResponse(data=resources, count=count, message=get_comment_success)

    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )


@router.put("/{comment_id}", response_model=DataResponse)
@inject
async def update(
    ctx_req_: Request,
    comment_id: str,
    req_: UpdateCommentRequestV1,
    svc: Annotated[CommentSVC, Depends(Provide[Container.comment_svc])],
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        # get user id from context request
        user_id = ctx_req_.state.user_id

        # validate request body
        try:
            UUID4(comment_id)
            req_.validate_()
        except Exception as exc:
            logger.error(exc)
            res = DataResponse(message=common_validation_error)
            return ORJSONResponse(
                status_code=common_validation_error.status_code,
                content=jsonable_encoder(res),
            )

        # convert request body to payload
        payload = req_.to_payload()
        payload.id_ = comment_id
        payload.owner_id = str(user_id)

        # execute
        error_ = await svc.update(payload=payload)
        if error_:
            if isinstance(error_, UpdateCommentException):
                res = DataResponse(message=update_comment_fail)
            elif isinstance(error_, UnauthorizeException):
                res = DataResponse(message=common_no_permission_error)
        else:
            res = DataResponse(message=update_comment_success)

    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )


@router.delete("/{comment_id}", response_model=DataResponse)
@inject
async def delete(
    ctx_req_: Request,
    comment_id: str,
    svc: Annotated[CommentSVC, Depends(Provide[Container.comment_svc])],
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        # get user id from context request
        user_id = ctx_req_.state.user_id

        # validate request body
        try:
            UUID4(comment_id)
        except Exception as exc:
            logger.error(exc)
            res = DataResponse(message=common_validation_error)
            return ORJSONResponse(
                status_code=common_validation_error.status_code,
                content=jsonable_encoder(res),
            )

        # build payload
        payload = DeleteCommentPayload(id_=comment_id, owner_id=str(user_id))

        # execute
        error_ = await svc.delete(payload=payload)
        if error_:
            if isinstance(error_, DeleteCommentException):
                res = DataResponse(message=delete_comment_fail)
            elif isinstance(error_, UnauthorizeException):
                res = DataResponse(message=common_no_permission_error)
        else:
            res = DataResponse(message=delete_comment_success)

    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )
