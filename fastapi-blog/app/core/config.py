# Manages application configuration such as environment variables,
# database connection strings, and external service settings.
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field(...)
    CLERK_ISSUER: str
    CLERK_JWKS_URL: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # or "allow" if you want to access unknown extras


settings = Settings()
