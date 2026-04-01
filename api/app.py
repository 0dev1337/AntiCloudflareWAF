from fastapi import FastAPI

from api.middleware import setup_logging_middleware
from api.routes.waf import router as waf_router


def create_app() -> FastAPI:
    app = FastAPI(title="AntiCloudflareWAF API", version="0.1.0")
    setup_logging_middleware(app)
    app.include_router(waf_router)
    return app

