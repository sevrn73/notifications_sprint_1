import backoff

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Настройки проекта
    """

    PG_HOST: str = Field("notification_db", env="BACKEND_DB_HOST")
    PG_PORT: int = Field(5432, env="BACKEND_DB_PORT")
    PG_USER: str = Field("postgres", env="BACKEND_DB_USER")
    PG_PASSWORD: int = Field(1234, env="BACKEND_DB_PASSWORD")
    DB_NAME: str = Field("notification", env="BACKEND_DB_NAME")
    RESTART_TIME: int = Field(5, env="TIME_TO_RESTART")
    API_URL: str = Field("http://notification_api:8010/app/v1/notification/send_notification", env="API_URL")


BACKOFF_CONFIG = {
    "wait_gen": backoff.expo,
    "exception": Exception,
    "max_tries": 10,
}

settings = Settings()
