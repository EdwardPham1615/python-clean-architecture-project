import grpc.aio

from internal.controllers.grpc.protos import post_v1_pb2, post_v1_pb2_grpc
from internal.controllers.http.resources import GetPostResourceV1
from internal.domains.entities import CreatePostPayload
from internal.patterns import Container
from utils.logger_utils import get_shared_logger

logger = get_shared_logger()


class PostPRouter(post_v1_pb2_grpc.PostV1Servicer):
    def __init__(self, container: Container):
        self._container = container

    async def Create(
        self,
        request: post_v1_pb2.CreatePostRequest,
        context: grpc.aio.ServicerContext,
    ) -> post_v1_pb2.CreatePostResponse:
        _post_svc = self._container.post_svc()

        # convert request body to payload
        payload = CreatePostPayload(
            text_content=request.text_content,
            owner_id=request.owner_id,
        )

        try:
            # execute
            (new_post, error_) = await _post_svc.create(payload=payload)
            if error_:
                raise error_

            return post_v1_pb2.CreatePostResponse(id=str(new_post.id_))
        except Exception as exc:
            logger.opt(exception=True).error(exc)
            raise exc

    async def GetById(
        self,
        request: post_v1_pb2.GetPostByIdRequest,
        context: grpc.aio.ServicerContext,
    ) -> post_v1_pb2.GetPostByIdResponse:
        _post_svc = self._container.post_svc()

        try:
            # execute
            (post_, error_) = await _post_svc.get_by_id(id_=request.id)
            if error_:
                raise error_

            resource = GetPostResourceV1()
            resource.from_entity(entity=post_)

            return post_v1_pb2.GetPostByIdResponse(
                id=resource.id_,
                text_content=resource.text_content,
                created_at=resource.created_at,
                updated_at=resource.updated_at,
            )
        except Exception as exc:
            logger.opt(exception=True).error(exc)
            raise exc
