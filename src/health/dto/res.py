from typing import Optional

from src.shared.dto.ResponseBase import ResponseBase
from src.shared.dto.PaginatedResponseBase import PaginatedResponseBase
from src.health.dto.main import CacheHealthCheckDto


class CacheHealthCheckListResDto(PaginatedResponseBase):
    health_checks: list[CacheHealthCheckDto]

class CacheHealthCheckResDto(ResponseBase):
    """Response DTO cho cache health check."""
    message: str = "CACHE OK"

class LatestCacheHealthCheckResDto(ResponseBase):
    health_check: Optional[CacheHealthCheckDto]
