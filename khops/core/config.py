"""Application Configuration"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    MODEL_SERVER_HOST: str = "0.0.0.0"
    MODEL_SERVER_PORT: int = 8001
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite:///./data/khops.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./data/artifacts"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None

    # Registry
    REGISTRY_PATH: str = "./data/registry"
    MODEL_REGISTRY_PATH: str = "./data/models"

    # Pipeline Execution
    PIPELINE_MAX_PARALLEL_NODES: int = 5
    PIPELINE_TIMEOUT_SECONDS: int = 3600
    EXECUTION_TIMEOUT_SECONDS: int = 3600
    EXECUTION_MAX_RETRIES: int = 3
    EXECUTION_RETRY_DELAY_SECONDS: int = 10

    # Observability
    OBSERVABILITY_ENABLED: bool = True
    METRICS_ENABLED: bool = True
    TRACES_ENABLED: bool = False
    LOGS_ENABLED: bool = True

    # Logging
    LOG_TO_FILE: bool = True
    LOG_FILE_PATH: str = "./logs/khops.log"
    LOG_MAX_BYTES: int = 10485760
    LOG_BACKUP_COUNT: int = 5

    # Scheduler
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "UTC"
    SCHEDULER_POOL_SIZE: int = 5

    # Security (Future)
    AUTH_ENABLED: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
