from fastapi import APIRouter

from src.health.router.health_check import router as router_health


main_router = APIRouter()
main_router.include_router(router_health)
