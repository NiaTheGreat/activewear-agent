from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = "postgresql+asyncpg://agent_user:agent_password@localhost:5432/manufacturer_agent"
    DATABASE_URL_SYNC: str = ""
    SECRET_KEY: str = "change-me-in-production"
    ANTHROPIC_API_KEY: str = ""
    BRAVE_API_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @model_validator(mode="after")
    def fix_database_urls(self):
        """Normalize DATABASE_URL for asyncpg and derive sync URL if missing.

        Railway provides DATABASE_URL as postgres:// which needs conversion
        to postgresql+asyncpg:// for SQLAlchemy async and postgresql:// for Alembic.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if not url.startswith("postgresql+asyncpg://"):
            self.DATABASE_URL = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if not self.DATABASE_URL_SYNC:
            self.DATABASE_URL_SYNC = self.DATABASE_URL.replace(
                "postgresql+asyncpg://", "postgresql://", 1
            )
        return self


settings = Settings()
