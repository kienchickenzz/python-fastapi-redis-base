from datetime import datetime

from pydantic import field_serializer

from src.shared.dto.ResponseBase import ResponseBase


class CacheHealthCheckDto(ResponseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_dates(self, value: datetime) -> str:
        return value.isoformat() if value else None # type: ignore
