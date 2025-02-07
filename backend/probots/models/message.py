import pydantic
from .mixins.pydantic_base import BaseSchema


class Message(BaseSchema):
    type: str
    event: str
    session_id: str
    data: dict

    @classmethod
    def from_json(cls, json: str) -> "Message":
        return cls.model_validate_json(json)
