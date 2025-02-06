import pydantic


class ErrorResponse(pydantic.BaseModel):
    message: str
