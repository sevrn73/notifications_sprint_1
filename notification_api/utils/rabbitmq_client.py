import json
from abc import ABC, abstractmethod
import logging

import aio_pika
import backoff
from fastapi import HTTPException

from dependencies.config import Settings, get_settings, BACKOFF_CONFIG
from utils.json_encoder import new_default


json.JSONEncoder.default = new_default

logger = logging.getLogger(__name__)

BACKOFF_CONFIG.update({"logger": logger})


class State(ABC):
    """ Базовый интерфейс состояния данных"""

    @abstractmethod
    def send_rabbitmq(self, message: dict, queue: str) -> None:
        pass

    @abstractmethod
    def close(self,) -> None:
        pass


class RabbitMQState(State):
    """
    Класс-интерфейс для работы с rabbitmq
    """

    def __init__(self, settings: Settings) -> None:
        """
        Parameters
        ----------
        :param settings: настройки проекта
        -------
        """
        self.settings = settings
        self._conn = None

    async def initialize(self):
        """
        Метод инициализации очередей
        """
        connection = await self.connect()
        async with connection:
            channel = await connection.channel()

            await channel.declare_queue(self.settings.email_queue, durable=True)
            await channel.declare_queue(self.settings.group_queue, durable=True)

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def connect(self):
        """
        Установка соединения с RabbitMQ
        """
        try:
            _conn = await aio_pika.connect_robust(
                f"amqp://{self.settings.rabbitmq_user}:{self.settings.rabbitmq_pass}@{self.settings.rabbitmq_host}/"
            )
            return _conn
        except (aio_pika.exceptions.AMQPError, ConnectionError):
            logger.info(f"RabbitMQ connection error")
            raise HTTPException(status_code=404, detail="RabbitMQ ConnectionError")

    async def _publish_rabbitmq(self, message: dict, queue: str) -> None:
        """
        Публикация сообщения в очередь RabbitMQ

        Parameters
        ----------
        :param message: сообщение
        :param queue: очередь
        -------
        """
        connection = await self.connect()
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                name=self.settings.message_exchange, durable=True,
            )
            await exchange.publish(
                aio_pika.Message(json.dumps(message).encode("utf-8")), routing_key=queue
            )

            logger.info(f"Message send to {queue}")

    async def send_rabbitmq(self, message: dict, queue: str) -> None:
        """
        Публикация сообщения в очередь RabbitMQ

        Parameters
        ----------
        :param message: сообщение
        :param queue: очередь
        -------
        """
        await self._publish_rabbitmq(message, queue)

    async def close(self) -> None:
        """
        Закрытие соединения с RabbitMQ
        """
        if self._conn:
            connect_status = await self._conn.is_open
            if connect_status:
                logging.debug("Close RabbitMQ connection")
                await self._conn.close()


settings = get_settings()
rabbitmq_client = RabbitMQState(settings)
