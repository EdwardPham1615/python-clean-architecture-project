from typing import Optional, Annotated

from pydantic import BaseModel, Field, UUID4, ValidationError

from internal.domains.entities import (
    CreateCommentPayload,
    UpdateCommentPayload,
)


class CreateCommentRequestV1(BaseModel):
    text_content: str = Field(description="Text content of comment")
    post_id: str = Field(description="ID of the post")

    def validate_(self):
        try:
            UUID4(self.post_id)
        except Exception as exc:
            raise ValidationError(exc)

    def to_payload(self) -> CreateCommentPayload:
        return CreateCommentPayload(
            text_content=self.text_content,
            post_id=self.post_id,
        )


class UpdateCommentRequestV1(BaseModel):
    text_content: Optional[
        Annotated[str, Field(description="Text content of comment")]
    ] = None

    def validate_(self):
        return self

    def to_payload(self) -> UpdateCommentPayload:
        return UpdateCommentPayload(
            text_content=self.text_content,
        )
