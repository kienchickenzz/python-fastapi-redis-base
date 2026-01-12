from fastapi import APIRouter, Depends

from src.shared.dependency_injection import Injects
from src.health.doc import Tags
from src.health.service.health_check import HealthCheckService
from src.health.dto.res import CacheHealthCheckResDto, CacheHealthCheckListResDto, LatestCacheHealthCheckResDto
from src.health.dto.req import GetPaginatedCacheHealthCheckReq


router = APIRouter(tags=[Tags.HEALTH], prefix="/health")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post(
    "/cache",
    summary="Cache Health Check",
    description="Check the health status of the cache connection.",
    response_model=CacheHealthCheckResDto,
)
async def check_cache_health(
    health_check_service: HealthCheckService = Injects("health_check_service"),
) -> CacheHealthCheckResDto:
    """
    Check the health status of the cache connection.
    """
    await health_check_service.check_cache_health()
    return CacheHealthCheckResDto()


@router.get(
    "/cache",
    summary="Get Cache Health Status",
    description="Retrieve the current health status of the cache.",
    response_model=CacheHealthCheckListResDto,
)
async def get_cache_health(
    req : GetPaginatedCacheHealthCheckReq = Depends(GetPaginatedCacheHealthCheckReq.as_query),
    health_check_service: HealthCheckService = Injects("health_check_service"),
) -> CacheHealthCheckListResDto:
    """
    Retrieve the current health status of the cache.
    """
    target_page = req.target_page
    page_size = req.page_size

    result = await health_check_service.get_cache_health_checks(
        target_page=target_page,
        page_size=page_size,
    )
    return result


@router.get(
    "/cache/latest",
    summary="Get Latest Cache Status",
    description="Retrieve the latest status of the cache.",
    response_model=LatestCacheHealthCheckResDto,
)
async def get_latest_cache_status(
    health_check_service: HealthCheckService = Injects("health_check_service"),
) -> LatestCacheHealthCheckResDto:
    """
    Retrieve the latest status of the cache.
    """
    result = await health_check_service.get_latest_cache_health_check()
    return result
