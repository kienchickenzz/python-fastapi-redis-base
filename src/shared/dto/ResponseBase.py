from pydantic import BaseModel, ConfigDict
from humps import camelize

class ResponseBase(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        alias_generator=camelize,
        populate_by_name=True,
        validate_assignment=True,
        extra='ignore',
        from_attributes=True
    )