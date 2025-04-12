from pydantic import BaseModel, ValidationError

from internal.domains.constants import V1ReBACRelation


class PermEntity(BaseModel):
    target_obj: str
    relation: str
    request_obj: str


class CreateSinglePermPayload(BaseModel):
    target_obj: str
    relation: V1ReBACRelation
    request_obj: str

    def validate_(self):
        if self.target_obj == "":
            raise ValidationError("Empty target_obj")
        else:
            split_target_obj = self.target_obj.split(":")
            if len(split_target_obj) == 1:
                raise ValidationError(
                    "target_obj must follow pattern: <object_type:id>"
                )

        if self.request_obj == "":
            raise ValidationError("Empty request_obj")
        else:
            split_request_obj = self.request_obj.split(":")
            if len(split_request_obj) == 1:
                raise ValidationError(
                    "request_obj must follow pattern: <object_type:id>"
                )

    def to_entity(self) -> PermEntity:
        return PermEntity(
            target_obj=self.target_obj,
            relation=self.relation.value,
            request_obj=self.request_obj,
        )
