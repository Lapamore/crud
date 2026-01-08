from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    redis_url: str = "redis://redis:6379/0"
    users_database_url: str
    main_database_url: str
    push_url: str = "http://push-notificator:8000/api/v1/notify"
    backend_url: str = "http://backend:8000"
    internal_api_key: str = ""

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls()


config = AppConfig.from_env()

