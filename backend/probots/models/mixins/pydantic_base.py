import pydantic
import pydantic.alias_generators


class BaseSchema(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel,
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
    )

    def as_msg(self):
        """Just a helper alias to standardize serialization for sending as a message payload"""
        return self.model_dump(by_alias=True)

    def as_response(self):
        """Just a helper alias to standardize serialization for sending as response payload"""
        return self.model_dump_json(by_alias=True)
