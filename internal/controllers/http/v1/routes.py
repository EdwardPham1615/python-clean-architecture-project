from fastapi import APIRouter

from internal.controllers.http.v1.endpoints import (
    authentication_router,
    comment_router,
    post_router,
)

api_router = APIRouter()
api_router.include_router(post_router, prefix="/posts", tags=["post"])
api_router.include_router(comment_router, prefix="/comments", tags=["comment"])
api_router.include_router(
    authentication_router, prefix="/authentication", tags=["authentication"]
)
