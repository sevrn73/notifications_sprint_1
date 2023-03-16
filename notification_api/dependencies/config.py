from functools import lru_cache

import backoff
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    project_name: str = Field("notification", env="PROJECT_NAME")

    jwt_secret_key: str = Field("test", env="JWT_SECRET_KEY")

    rabbitmq_host: str = Field("localhost", env="RABBITMQ_HOST")
    rabbitmq_user: str = Field("user", env="RABBITMQ_DEFAULT_USER")
    rabbitmq_pass: str = Field("pass", env="RABBITMQ_DEFAULT_PASS")

    email_exchange: str = Field("email", env="RABBIT_SEND_EMAIL_QUEUE_EXCHANGE")
    group_exchange: str = Field("group_chunk", env="RABBIT_CONSUME_QUEUE_EXCHANGE")
    email_queue: str = Field("send_email", env="RABBIT_SEND_EMAIL_QUEUE")
    group_queue: str = Field("group_chunk", env="RABBIT_CONSUME_QUEUE")
    message_exchange: str = Field("notifications_exchange", env="RABBIT_EXCHANGE")


BACKOFF_CONFIG = {
    "wait_gen": backoff.expo,
    "exception": Exception,
    "max_tries": 10,
}


@lru_cache()
def get_settings() -> Settings:
    """
    Инициализация настроек проекта

    Returns
    -------
    :return: настройки проекта
    """
    return Settings()
