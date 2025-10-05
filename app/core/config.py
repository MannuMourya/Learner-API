from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator, Field
import secrets
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Learner API"
    ENVIRONMENT: str = "dev"

    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_hex(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    API_V1_PREFIX: str = ""

    ALLOWED_ORIGINS: List[AnyHttpUrl] | List[str] = ["*"]

    RATE_LIMIT_REQ: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    DATA_DIR: str = "/data"

    # DB
    POSTGRES_DB: str = "learner_api"
    POSTGRES_USER: str = "learner"
    POSTGRES_PASSWORD: str = "learnerpwd"
    DATABASE_URL: str = "postgresql+psycopg2://learner:learnerpwd@db:5432/learner_api"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 2
    LOG_LEVEL: str = "info"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def split_csv(cls, v):
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

settings = Settings()
