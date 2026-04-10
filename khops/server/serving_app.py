"""FastAPI application for dedicated model serving."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from khops.core.config import settings
from khops.server.routes.serving import router as serving_router
from khops.server.routes.observability import router as observability_router
from khops.server.routes.registry import router as registry_router
from khops.core.logging import setup_logging
from khops.db.session import init_db
from khops.db.base import Base
from khops.db.session import engine

logger = logging.getLogger(__name__)
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 KHOps Model Serving starting up...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    yield
    logger.info("🛑 KHOps Model Serving shutting down...")


app = FastAPI(
    title="KHOps Model Serving",
    description="Dedicated model serving API for registered models",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(serving_router, prefix="/api/v1", tags=["serving"])
app.include_router(observability_router, prefix="/api/v1", tags=["observability"])
app.include_router(registry_router, prefix="/api/v1", tags=["registry"])


@app.get("/")
async def root():
    return {
        "name": "KHOps Model Serving",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception in model serving: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
