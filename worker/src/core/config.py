import logging.config
from enum import Enum

from pydantic import BaseSettings, Field

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {
            "format": "%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
        },
    },
    "handlers": {
        "stream_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default_formatter",
        },
    },
    "loggers": {
        "__main__": {"handlers": ["stream_handler"], "level": "INFO", "propagate": True},
        "services.db": {"handlers": ["stream_handler"], "level": "INFO", "propagate": True},
        "services.rabbit": {"handlers": ["stream_handler"], "level": "INFO", "propagate": True},
        "services.render": {"handlers": ["stream_handler"], "level": "INFO", "propagate": True},
        "services.sender": {"handlers": ["stream_handler"], "level": "INFO", "propagate": True},
    },
}
logging.config.dictConfig(LOGGING_CONFIG)


class RabbitPublisher(BaseSettings):
    exchange: str = Field("send_email", env="RABBIT_SEND_EMAIL_QUEUE_EXCHANGE")
    exchange_type: str = Field("direct", env="RABBIT_SEND_EMAIL_QUEUE_EXCHANGE_TYPE")
    queue: str = Field("send_email", env="RABBIT_SEND_EMAIL_QUEUE")
    durable: str = Field("True", env="RABBIT_SEND_EMAIL_QUEUE_DURABLE")


class RabbitConsumer(BaseSettings):
    exchange: str = Field("group_chunk", env="RABBIT_CONSUME_QUEUE_EXCHANGE")
    exchange_type: str = Field("direct", env="RABBIT_CONSUME_QUEUE_EXCHANGE_TYPE")
    queue: str = Field("group_chunk", env="RABBIT_CONSUME_QUEUE")
    durable: str = Field("True", env="RABBIT_CONSUME_QUEUE_DURABLE")


class EmailSettings(BaseSettings):
    address: str = Field(..., env="EMAIL_SERVER_ADDRESS")
    port: int = Field(..., env="EMAIL_SERVER_PORT")
    login: str = Field(..., env="EMAIL_ACCOUNT_LOGIN")
    password: str = Field(..., env="EMAIL_ACCOUNT_PASSWORD")


class NotificationStatus(Enum):
    waiting = "waiting"
    processing = "processing"
    done = "done"


class Settings(BaseSettings):
    rabbit_host: str = Field("rabbitmq", env="RABBITMQ_HOST")
    rabbit_user: str = Field("user", env="RABBITMQ_DEFAULT_USER")
    rabbit_password: str = Field("pass", env="RABBITMQ_DEFAULT_PASS")
    rabbit_consumer: RabbitConsumer = RabbitConsumer()
    rabbit_publisher: RabbitPublisher = RabbitPublisher()
    email_settings: EmailSettings = EmailSettings()

    notification_db_host: str = Field("db", env="BACKEND_DB_HOST")
    notification_db_port: int = Field(5432, env="BACKEND_DB_PORT")
    notification_db_user: str = Field("postgres", env="BACKEND_DB_USER")
    notification_db_password: str = Field("1234", env="BACKEND_DB_PASSWORD")
    notification_db_name: str = Field("notification", env="BACKEND_DB_NAME")

    url_service_user: str = Field("http://auth/user_info", env="API_USER_INFO")

    chunk_size: int = 50


settings = Settings()
