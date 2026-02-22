from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth, chat, health, schema
from src.config.settings import get_settings
from src.db.adapters.factory import get_adapter
from src.utils.db import check_db_connection

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect the database adapter on startup, disconnect on shutdown."""
    adapter = get_adapter()
    await adapter.connect()
    
    # Verify the connection is actually alive before accepting traffic
    await check_db_connection(adapter)
    
    yield
    await adapter.disconnect()
    
    from src.cache.redis_client import close_redis
    await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(
        title="DeepAgent SQL Chat API",
        version="0.1.0",
        docs_url="/docs" if settings.app_env != "production" else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router,   prefix="/api")
    app.include_router(chat.router,   prefix="/api")
    app.include_router(health.router, prefix="/api")
    app.include_router(schema.router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
    )
