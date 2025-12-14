from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    REDIS_URL: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
