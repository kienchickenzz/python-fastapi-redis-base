import json
from datetime import datetime

from redis.asyncio import Redis

from src.health.dto.main import CacheHealthCheckDto
from src.health.dto.res import CacheHealthCheckListResDto, LatestCacheHealthCheckResDto


class HealthCheckService:
    """Service class for health check operations."""

    def __init__(self, cache_redis_client: Redis) -> None:
        self._cache_redis_client = cache_redis_client

    async def check_cache_health(self) -> None:
        """
        Tạo và lưu bản ghi health check vào Redis.
        Lưu toàn bộ object CacheHealthCheckDto dạng JSON.
        """
        timestamp = datetime.now()
        health_check_id = int(timestamp.timestamp() * 1000)

        key = f"health:check:{timestamp.isoformat()}" # e.g., health:check:2026-01-12T10:30:45.123456

        health_check_dto = CacheHealthCheckDto(
            id=health_check_id,
            created_at=timestamp,
            updated_at=timestamp,
        )

        value = json.dumps(health_check_dto.model_dump(mode='json'))
        await self._cache_redis_client.set(
            name=key,
            value=value,
            ex=300 # 5 min
        )

    async def get_cache_health_checks(
        self,
        target_page: int,
        page_size: int,
    ):
        """
        Lấy danh sách cache health checks từ Redis với phân trang.

        Args:
            target_page: Trang cần lấy (bắt đầu từ 1)
            page_size: Số lượng records mỗi trang

        Returns:
            CacheHealthCheckListDto: DTO chứa health_checks, current_page, total_pages, page_size
        """

        # 1. Scan tất cả keys với pattern health:check:*
        keys = []
        cursor = 0
        pattern = "health:check:*"

        # Scan keys từ Redis (handle large dataset với cursor)
        while True:
            cursor, partial_keys = await self._cache_redis_client.scan(
                cursor=cursor,
                match=pattern,
                count=1000  # Scan 1000 keys mỗi lần
            )
            keys.extend([key.decode('utf-8') if isinstance(key, bytes) else key for key in partial_keys])

            if cursor == 0:  # Đã scan hết
                break

        # 2. Sort keys theo timestamp (descending - mới nhất trước)
        # Key format: health:check:2026-01-12T10:30:45.123456
        keys.sort(reverse=True)

        # 3. Tính toán pagination
        total_records = len(keys)
        total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 0

        # Nếu không có data
        if total_records == 0:
            return CacheHealthCheckListResDto(
                health_checks=[],
                current_page=target_page,
                total_pages=0,
                page_size=page_size
            )

        # Tính offset
        start_index = (target_page - 1) * page_size
        end_index = start_index + page_size

        # Lấy keys cho trang hiện tại
        page_keys = keys[start_index:end_index]

        # 4. Lấy values từ Redis và parse thành DTO
        health_checks = []

        for idx, key in enumerate(page_keys, start=start_index + 1):
            # Get value từ Redis
            value = await self._cache_redis_client.get(key)

            if value:
                # Parse value (nếu là bytes thì decode)
                if isinstance(value, bytes):
                    value = value.decode('utf-8')

                # Parse JSON thành dict
                data = json.loads(value)

                # Deserialize dict thành CacheHealthCheckDto
                # Pydantic sẽ tự động parse ISO string thành datetime
                health_check_dto = CacheHealthCheckDto(**data)

                health_checks.append(health_check_dto)

        return CacheHealthCheckListResDto(
            health_checks=health_checks,
            current_page=target_page,
            total_pages=total_pages,
            page_size=page_size
        )

    async def get_latest_cache_health_check(self) -> LatestCacheHealthCheckResDto:
        """
        Lấy health check mới nhất từ Redis.

        Returns:
            LatestCacheHealthCheckResDto: DTO chứa health check mới nhất

        Raises:
            ValueError: Nếu không tìm thấy health check nào trong Redis
        """
        # Scan tất cả keys với pattern health:check:*
        keys = []
        cursor = 0
        pattern = "health:check:*"

        # Scan keys từ Redis
        while True:
            cursor, partial_keys = await self._cache_redis_client.scan(
                cursor=cursor,
                match=pattern,
                count=1000
            )
            keys.extend([key.decode('utf-8') if isinstance(key, bytes) else key for key in partial_keys])

            if cursor == 0:
                break

        # Kiểm tra nếu không có data
        if not keys:
            return LatestCacheHealthCheckResDto(
                health_check=None
            )

        # Sort keys theo timestamp (descending) và lấy key mới nhất
        # Key format: health:check:2026-01-12T10:30:45.123456
        keys.sort(reverse=True)
        latest_key = keys[0]

        value = await self._cache_redis_client.get(latest_key)
        if not value:
            return LatestCacheHealthCheckResDto(
                health_check=None
            )

        # Parse value
        if isinstance(value, bytes):
            value = value.decode('utf-8')

        data = json.loads(value)
        health_check_dto = CacheHealthCheckDto(**data)
        return LatestCacheHealthCheckResDto(
            health_check=health_check_dto
        )
