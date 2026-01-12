from threading import Lock
from types import TracebackType
from typing import Dict, Optional, Type

from redis.asyncio import Redis, ConnectionPool

from src.shared.config import Config


class CacheRedisClientFactory:
    """
    Factory quản lý kết nối Redis với cơ chế singleton cho mỗi database identifier.
    
    Để tạo Redis client, bạn cần các biến môi trường:
        <<cache_identifier>>_HOST
        <<cache_identifier>>_PORT
        <<cache_identifier>>_DB (tuỳ chọn, mặc định là 0)
        <<cache_identifier>>_PASSWORD (tuỳ chọn)
    
    Factory này đã được quản lý context bởi FastAPIInitializer.
    
    Ví dụ sử dụng:
    >>> class MyInitializer(Initializer):
    ...     def __init__(self, app: FastAPI) -> None:
    ...         super().__init__(app)
    ...         self.cache_client: Optional[Redis] = None
    ...
    ...     async def __aenter__(self) -> MyInitializer:
    ...         await super().__aenter__()
    ...         self.cache_client = self.cache_factory.create_client("MY_CACHE")
    ...
    ...     async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
    ...         await super().__aexit__(exc_type, exc_val, exc_tb)
    """

    def __init__(self, *, config: Config):
        self._config = config
        self._client_init_lock: Lock = Lock()
        self._clients: Dict[str, Redis] = {}
        self._pools: Dict[str, ConnectionPool] = {}

    async def __aenter__(self) -> "CacheRedisClientFactory":
        return self

    async def __aexit__(
        self, 
        exc_type: Optional[Type[BaseException]], 
        exc_val: Optional[BaseException], 
        exc_tb: Optional[TracebackType]
    ) -> None:
        # Đóng tất cả clients và connection pools
        for client in self._clients.values():
            await client.aclose()
        
        for pool in self._pools.values():
            await pool.aclose()

    def create_client(self, cache_identifier: str) -> Redis:
        """
        Tạo hoặc lấy Redis client từ cache.
        
        Args:
            cache_identifier: Định danh duy nhất cho Redis instance
            
        Returns:
            Redis client instance
        """
        with self._client_init_lock:
            if cache_identifier not in self._clients:
                self._clients[cache_identifier] = self._create_redis_client(
                    cache_identifier.upper()
                )
        
        return self._clients[cache_identifier]

    def _create_redis_client(self, cache_identifier: str) -> Redis:
        """
        Tạo Redis client mới.
        
        Args:
            cache_identifier: Định danh Redis (viết hoa)
            
        Returns:
            Redis client được cấu hình
        """
        # Lấy thông tin cấu hình từ config
        host = self._config.require_config(f"{cache_identifier}_HOST")
        port = self._config.require_config(f"{cache_identifier}_PORT")
        
        # Các tham số tuỳ chọn
        db = self._config.get_int(f"{cache_identifier}_DB", 0)
        password = self._config.get_config(f"{cache_identifier}_PASSWORD", "")
        
        # Tạo connection pool
        pool = ConnectionPool(
            host=host,
            port=int(port),
            db=int(db),
            password=password,
            decode_responses=True,  # Tự động decode responses sang string
            max_connections=10      # Giới hạn số connection trong pool
        )
        
        # Lưu pool để quản lý lifecycle
        self._pools[cache_identifier] = pool
        
        # Tạo và trả về Redis client
        return Redis(
            connection_pool=pool,
            # Các tuỳ chọn bổ sung nếu cần
            # retry_on_timeout=True,
            # socket_keepalive=True,
        )