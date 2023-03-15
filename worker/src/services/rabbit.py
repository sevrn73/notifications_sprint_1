import logging
from abc import ABC, abstractmethod

import backoff
import pika

logger = logging.getLogger(__name__)


class Rabbit(ABC):
    def __init__(self, host, user, password, rabbit_settings) -> None:
        super().__init__()

        self.host = host
        self.user = user
        self.password = password
        credentials = pika.PlainCredentials(self.user, self.password)

        self.parameters = pika.ConnectionParameters(host=self.host, credentials=credentials)
        self.connection = None
        self.channel = None
        self.rabbit_settings = rabbit_settings

    @backoff.on_exception(backoff.expo, pika.exceptions.AMQPConnectionError)
    def connect(self) -> None:
        if not self.connection:
            logger.info("Connect rabbit")
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
        self.init_channel()

    def init_channel(self):
        self.channel.exchange_declare(
            exchange=self.rabbit_settings.exchange,
            exchange_type=self.rabbit_settings.exchange_type,
            durable=self.rabbit_settings.durable,
        )

        self.channel.queue_declare(queue=self.rabbit_settings.queue, durable=self.rabbit_settings.durable)
        self.channel.queue_bind(exchange=self.rabbit_settings.exchange, queue=self.rabbit_settings.queue)

    def listen_channel(self, message_callback, auto_ack=True):
        self.channel.basic_consume(
            queue=self.rabbit_settings.queue, on_message_callback=message_callback, auto_ack=auto_ack
        )

        logger.info("Waiting for messages")
        self.channel.start_consuming()


class RabbitConsumer(Rabbit):
    def __init__(self, host, user, password, rabbit_settings) -> None:
        super().__init__(host, user, password, rabbit_settings)


class RabbitPublisher(Rabbit):
    def __init__(self, host, user, password, rabbit_settings) -> None:
        super().__init__(host, user, password, rabbit_settings)

    def publish(self, message):
        self.channel.basic_publish(
            exchange=self.rabbit_settings.exchange,
            routing_key=self.rabbit_settings.queue,
            body=message,
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )
        logger.info("Sent %r" % message)
