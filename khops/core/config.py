"""Application Configuration

Configuration hierarchy (highest to lowest precedence):
1. Environment variables (with KHOPS_ prefix)
2. YAML config file (dev.yaml, prod.yaml, or default.yaml)
3. .env file
4. Hard-coded defaults in this file

Usage:
    from khops.core.config import settings
    print(settings.SERVER_PORT)

Environment-based loading:
    ENVIRONMENT=dev    -> loads configs/dev.yaml
    ENVIRONMENT=prod   -> loads configs/prod.yaml
    ENVIRONMENT=default -> loads configs/default.yaml (no env var = default)

Override example:
    SERVER_PORT=9000 ENVIRONMENT=dev python app.py
    # Will use dev.yaml settings but override SERVER_PORT to 9000
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic_settings import BaseSettings


def load_yaml_config(environment: str = "dev") -> Dict[str, Any]:
    """Load YAML configuration file for the specified environment.

    Args:
        environment: Environment name (dev, prod, or default)

    Returns:
        Dictionary of configuration values from YAML file
    """
    # Determine config file path
    config_dir = Path(__file__).parent.parent.parent / "configs"
    config_file = config_dir / f"{environment}.yaml"

    # Fall back to default if specific environment file doesn't exist
    if not config_file.exists():
        config_file = config_dir / "default.yaml"

    # Load and parse YAML
    if config_file.exists():
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f) or {}
            return config_data

    return {}


class Settings(BaseSettings):
    """Application settings with YAML and environment variable support"""

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    MODEL_SERVER_HOST: str = "0.0.0.0"
    MODEL_SERVER_PORT: int = 8001
    MODEL_SERVER_PORT_STAGING: int = 8002
    MODEL_SERVER_PORT_PRODUCTION: int = 8003
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql://khops:khops_dev@localhost:5432/khops"
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

    # Environment info
    ENVIRONMENT: str = "dev"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @classmethod
    def settings_customizer(
        cls, settings: BaseSettings, init_settings, env_settings, dotenv_settings
    ) -> BaseSettings:
        """Custom settings loader supporting YAML configuration files.

        Priority (highest to lowest):
        1. Environment variables with KHOPS_ prefix
        2. YAML config file
        3. .env file
        4. Defaults in class definition
        """
        # Get environment from env vars or default
        environment = env_settings.get("ENVIRONMENT", "dev")

        # Load YAML config for the environment
        yaml_config = load_yaml_config(environment)

        # Merge settings: env vars > yaml > dotenv > defaults
        # Start with dotenv settings
        merged = dict(dotenv_settings)

        # Apply YAML settings (lower priority than env vars)
        merged.update(yaml_config)

        # Env vars are already in env_settings (highest priority)
        # They will be applied by Pydantic after this method returns

        return init_settings or merged


def get_settings() -> Settings:
    """Get or create the global settings instance.

    Returns:
        Settings instance with configuration from all sources
    """
    return Settings(
        _env_file=".env", _case_sensitive=True, **load_yaml_config(os.getenv("ENVIRONMENT", "dev"))
    )


# Global settings instance
settings = Settings(**load_yaml_config(os.getenv("ENVIRONMENT", "dev")))
