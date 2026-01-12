from types import TracebackType
from typing import Optional, Type

from fastapi import FastAPI
from redis.asyncio import Redis

from src.shared.initializer import State, Initializer
from src.health.service.health_check import HealthCheckService


class ServiceState(State):
    # Services
    health_check_service: HealthCheckService
    # Repositories
    cache_redis_client: Redis

class HealthInitializer(Initializer):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app=app)

    async def __aenter__(self) -> ServiceState:
        state = await super().__aenter__()

        # DB engine
        cache_redis_client = self.cache_redis_client_factory.create_client("CACHE")

        # Initialize utilities

        # Initialize repositories

        # Initialize services/tools
        health_check_service = HealthCheckService(
            cache_redis_client=cache_redis_client,
        )
        
        return ServiceState(
            **state,
            cache_redis_client=cache_redis_client,
            health_check_service=health_check_service,
        )

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        # self.logger.info("detector_service_stopped")
