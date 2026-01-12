from os import environ

from dotenv import load_dotenv
from fastapi import APIRouter

from src.shared.app import create_fastapi_app
from src.shared.config import Config

from src.health.health_initializer import HealthInitializer
from src.health.router.main import main_router as router_health
from src.health.doc import Tags


load_dotenv('.env')
config = Config(environ)

app = create_fastapi_app(
    config=config,
    initializer=HealthInitializer,
    title="Automatic Market Report",
    description="Automated market analyze service",
    version="0.1.0",
    team_name="core",
    team_url="https://invalid-address.ee",
    openapi_tags=Tags.get_docs(),
)

# Service routes
main_router = APIRouter(prefix="/api")
main_router.include_router(router_health)
app.include_router(main_router)
