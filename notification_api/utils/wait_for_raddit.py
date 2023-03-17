import asyncio
import logging

import aio_pika
import backoff

from dependencies.config import Settings, get_settings, BACKOFF_CONFIG


logger = logging.getLogger(__name__)

BACKOFF_CONFIG.update({"logger": logger})


@backoff.on_exception(**BACKOFF_CONFIG)
async def rabbit_connection(settings: Settings) -> None:
    """
    Функция проверяющая соединение с RabbitMQ

    Parameters
    ----------
    :param settings: настройки проекта
    """
    connection = await aio_pika.connect_robust(
        f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_pass}@{settings.rabbitmq_host}/"
    )

    channel = await connection.channel()
    await connection.close()


if __name__ == "__main__":
    settings = get_settings()
    asyncio.run(rabbit_connection(settings))
    logger.info(f"Connected to RabbitMQ")
