from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    BUSINESS_DATABASE_URL: str = Field(..., env="BUSINESS_DATABASE_URL")
    # AUTH_SERVICE_URL: str = Field(..., env="AUTH_SERVICE_URL")

    class Config:
        env_file = ".env"

settings = Settings()
