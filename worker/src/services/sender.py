import json
import logging

from core.config import NotificationStatus
from jinja2 import Template
from models.message import Message
from pydantic import ValidationError
from services.db import NotificationsDb
from services.get_user import ApiUserInfoFake
from services.mail import EmailSMTP
from services.rabbit import RabbitPublisher

logger = logging.getLogger(__name__)


class Sender:
    def __init__(
        self,
        db_notification: NotificationsDb,
        rabbit_publisher: RabbitPublisher,
        email_notification: EmailSMTP,
    ):
        self.db = db_notification
        self.rabbit_publisher = rabbit_publisher
        self.email = email_notification
        self.api_user = ApiUserInfoFake("url_fake")

    @staticmethod
    def __template_render(template, context=None):
        if not context:
            context = {}
        template = Template(template)
        return template.render(context)

    def callback(self, ch, method, properties, body):
        try:
            message_rabbit = Message(**json.loads(body))
        except ValidationError as e:
            raise ValueError("Error structure message")
        template_raw = self.db.get_template(message_rabbit.template_id)

        if not template_raw:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            raise ValueError("Not Template")

        type_notification = template_raw.NotificationType
        template = template_raw.Template

        unsubscribe_user = [
            item.user
            for item in self.db.get_unsubscribe(type_notification.title, users_id=message_rabbit.context.users_id)
        ]
        ch.basic_ack(delivery_tag=method.delivery_tag)

        for user in message_rabbit.context.users_id:
            if user in unsubscribe_user:
                continue
            user_info = self.api_user.get_user(user)
            context_user = {**message_rabbit.context.payload.dict(), "username": user_info.user_name}
            message = self.__template_render(template.code, context_user)
            try:
                self.email.send(template.subject, user_info.user_email, message)
            except Exception as e:
                logger.error("Error send message to {}, message: {}".format(user_info, e))

        if message_rabbit.notification_id and message_rabbit.last_chunk:
            self.db.set_status_notification(message_rabbit.notification_id, NotificationStatus.done.value)
