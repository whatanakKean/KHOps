"""FastAPI Application"""

import logging
from contextlib import asynccontextmanager

import sqlalchemy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import khops.db.models
from khops.core.config import settings
from khops.core.logging import setup_logging
from khops.db.base import Base
from khops.db.session import engine, init_db
from khops.server.routes import health, metrics, models, pipelines, runs
from khops.server.routes.observability import router as observability
from khops.server.routes.projects import router as projects
from khops.server.routes.registry import router as registry

# Setup logging
logger = logging.getLogger(__name__)
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 KHOps Server starting up...")
    try:
        # Initialize database
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {str(e)}")

    yield

    logger.info("🛑 KHOps Server shutting down...")


# Create FastAPI application
app = FastAPI(
    title="KHOps",
    description="High-Performance MLOps Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
app.include_router(models.router, prefix="/api/v1", tags=["models"])
app.include_router(projects, prefix="/api/v1", tags=["projects"])
app.include_router(pipelines.router, prefix="/api/v1", tags=["pipelines"])
app.include_router(runs.router, prefix="/api/v1", tags=["runs"])
app.include_router(observability, prefix="/api/v1", tags=["observability"])
app.include_router(registry, prefix="/api/v1", tags=["registry"])


# Root endpoint
@app.get("/")
async def root():
    """Root API endpoint"""
    return {
        "name": "KHOps",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
    )
