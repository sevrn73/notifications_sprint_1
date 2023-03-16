import json
import logging
from functools import partial

from core.config import NotificationStatus, settings
from models.message import Context, Message, MessageBase, MessageChunk
from more_itertools import chunked
from services.db import NotificationsDb
from services.rabbit import RabbitConsumer, RabbitPublisher

logger = logging.getLogger(__name__)


class Render:
    def __init__(
        self,
        db_notification: NotificationsDb,
        rabbit_consumer: RabbitConsumer,
        rabbit_publisher: RabbitPublisher,
    ):
        self.db = db_notification
        self.rabbit_consumer = rabbit_consumer
        self.rabbit_publisher = rabbit_publisher

    @staticmethod
    def __generate_message(count_users, func_chunk, payload, message_base):
        count_response_user = 0
        for users in func_chunk():
            count_response_user += len(users)
            context = Context(payload=payload, users_id=users, group_id=None)

            new_message = Message(**message_base.dict(), context=context)
            if count_response_user >= count_users:
                new_message.last_chunk = True
            yield new_message

    def __chunk_group_to_users(self, group_id):
        offset = 0
        while True:
            result = self.db.get_users_from_group(group_id, settings.chunk_size, offset)
            list_user = [user.user_id for user in result]
            yield list_user
            if len(result) < settings.chunk_size:
                break
            offset += settings.chunk_size

    def callback(self, ch, method, properties, body):
        rabbit_message = MessageChunk(**json.loads(body))

        if rabbit_message.notification_id:
            self.db.set_status_notification(rabbit_message.notification_id, NotificationStatus.processing.value)
        ch.basic_ack(delivery_tag=method.delivery_tag)

        message_base = MessageBase(**rabbit_message.dict())
        group_id = rabbit_message.context.group_id

        chunk_users = partial(chunked, rabbit_message.context.users_id, settings.chunk_size)
        chunk_group = partial(self.__chunk_group_to_users, group_id)

        if rabbit_message.context.users_id:
            count_users = len(rabbit_message.context.users_id)
            chunk_function = chunk_users
        elif group_id:
            count_users = self.db.get_count_users_in_group(group_id)
            chunk_function = chunk_group

        for new_message in self.__generate_message(
            count_users,
            chunk_function,
            rabbit_message.context.payload,
            message_base,
        ):
            logger.info(new_message)
            self.rabbit_publisher.publish(json.dumps(new_message.dict()))
