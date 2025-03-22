from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from loguru import logger
from pydantic import ValidationError, UUID4, Field

from internal.patterns import Container
from internal.controllers.http.payloads import CreatePostRequestV1, UpdatePostRequestV1
from internal.controllers.http.resources import GetPostResourceV1, CreatePostResourceV1
from internal.controllers.responses import DataResponse
from internal.controllers.responses.error_code import (
    common_internal_error,
    common_validation_error,
    create_post_fail,
    get_post_fail,
    update_post_fail,
    delete_post_fail,
)
from internal.controllers.responses.success_code import (
    create_post_success,
    get_post_success,
    update_post_success,
    delete_post_success,
)
from internal.domains.entities import GetMultiPostsFilter
from internal.domains.errors import (
    CreatePostException,
    GetPostException,
    UpdatePostException,
    DeletePostException,
)
from dependency_injector.wiring import Provide, inject

from internal.domains.services import PostSVC

router = APIRouter()


@router.post("", response_model=DataResponse)
@inject
async def create(
    req_: CreatePostRequestV1,
    svc: Annotated[PostSVC, Depends(Provide[Container.post_svc])],
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
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

        # execute
        (new_post, error_) = await svc.create(payload=payload)
        if error_:
            if isinstance(error_, CreatePostException):
                res = DataResponse(message=create_post_fail)
        else:
            resource = CreatePostResourceV1()
            resource.from_entity(entity=new_post)
            res = DataResponse(data=[resource], count=1, message=create_post_success)

    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )


@router.get("/{post_id}", response_model=DataResponse)
@inject
async def get_by_id(
    post_id: str, svc: Annotated[PostSVC, Depends(Provide[Container.post_svc])]
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        # validate request body
        try:
            UUID4(post_id)
        except Exception as exc:
            logger.error(exc)
            res = DataResponse(message=common_validation_error)
            return ORJSONResponse(
                status_code=common_validation_error.status_code,
                content=jsonable_encoder(res),
            )

        # execute
        (post_, error_) = await svc.get_by_id(id_=post_id)
        if error_:
            if isinstance(error_, GetPostException):
                res = DataResponse(message=get_post_fail)
        else:
            resource = GetPostResourceV1()
            resource.from_entity(entity=post_)
            res = DataResponse(data=[resource], count=1, message=get_post_success)

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
    svc: Annotated[PostSVC, Depends(Provide[Container.post_svc])],
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
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        # validate request body
        try:
            filter_ = GetMultiPostsFilter(
                sort_field=sort_field,
                sort_order=sort_order,
                offset=offset,
                limit=limit,
                from_date=from_date,
                to_date=to_date,
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
        ((posts_, count), error_) = await svc.get_multi(filter_=filter_)
        if error_:
            if isinstance(error_, GetPostException):
                res = DataResponse(message=get_post_fail)
        else:
            resource = GetPostResourceV1()
            resources = [resource.from_entity(entity=post_) for post_ in posts_]
            res = DataResponse(data=resources, count=count, message=get_post_success)

    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )


@router.put("/{post_id}", response_model=DataResponse)
@inject
async def update(
    post_id: str,
    req_: UpdatePostRequestV1,
    svc: Annotated[PostSVC, Depends(Provide[Container.post_svc])],
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        # validate request body
        try:
            UUID4(post_id)
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
        payload.id_ = post_id

        # execute
        error_ = await svc.update(payload=payload)
        if error_:
            if isinstance(error_, UpdatePostException):
                res = DataResponse(message=update_post_fail)
        else:
            res = DataResponse(message=update_post_success)

    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )


@router.delete("/{post_id}", response_model=DataResponse)
@inject
async def delete(
    post_id: str,
    svc: Annotated[PostSVC, Depends(Provide[Container.post_svc])],
):
    # Default res
    res = DataResponse(message=common_internal_error)
    try:
        # validate request body
        try:
            UUID4(post_id)
        except Exception as exc:
            logger.error(exc)
            res = DataResponse(message=common_validation_error)
            return ORJSONResponse(
                status_code=common_validation_error.status_code,
                content=jsonable_encoder(res),
            )

        # execute
        error_ = await svc.delete(id_=post_id)
        if error_:
            if isinstance(error_, DeletePostException):
                res = DataResponse(message=delete_post_fail)
        else:
            res = DataResponse(message=delete_post_success)

    except Exception as exc:
        logger.error(exc)
        res = DataResponse(message=common_internal_error)

    return ORJSONResponse(
        status_code=res.message.status_code,
        content=jsonable_encoder(res),
    )
