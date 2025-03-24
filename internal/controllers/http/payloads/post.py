from typing import Annotated, Optional

from pydantic import BaseModel, Field

from internal.domains.entities import CreatePostPayload, UpdatePostPayload


class CreatePostRequestV1(BaseModel):
    text_content: str = Field(description="Text content of the post")

    def validate_(self):
        return self

    def to_payload(self) -> CreatePostPayload:
        return CreatePostPayload(
            text_content=self.text_content,
        )


class UpdatePostRequestV1(BaseModel):
    text_content: Optional[
        Annotated[str, Field(description="Text content of the post")]
    ] = None

    def validate_(self):
        return self

    def to_payload(self) -> UpdatePostPayload:
        return UpdatePostPayload(
            text_content=self.text_content,
        )
