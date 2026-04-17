# Manages application configuration such as environment variables,
# database connection strings, and external service settings.
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = Field(...)
    CLERK_ISSUER: str
    CLERK_JWKS_URL: str
    CLERK_WEBHOOK_SECRET: str
    DEBUG: bool = Field(default=False)
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM: str

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
