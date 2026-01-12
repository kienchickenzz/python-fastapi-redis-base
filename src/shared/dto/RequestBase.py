from pydantic import BaseModel, Field, ConfigDict, field_validator
from humps import camelize
from fastapi import Query


class RequestBase(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        alias_generator=camelize,
        populate_by_name=True,
        validate_assignment=True,
        extra='forbid',
    )
