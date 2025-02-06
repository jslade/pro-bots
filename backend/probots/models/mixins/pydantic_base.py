import pydantic
import pydantic.alias_generators


class BaseSchema(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
