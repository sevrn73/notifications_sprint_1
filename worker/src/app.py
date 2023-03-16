import logging

from core.config import settings
from services.db import NotificationsDb
from services.mail import EmailSMTP
from services.rabbit import RabbitConsumer, RabbitPublisher
from services.render import Render
from services.sender import Sender

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    db = NotificationsDb(
        user=settings.notification_db_user,
        password=settings.notification_db_password,
        host=settings.notification_db_host,
        port=settings.notification_db_port,
        db_name=settings.notification_db_name,
    )
    rabbit_consumer = RabbitConsumer(
        settings.rabbit_host,
        settings.rabbit_user,
        settings.rabbit_password,
        rabbit_settings=settings.rabbit_consumer,
    )
    rabbit_publisher = RabbitPublisher(
        settings.rabbit_host,
        settings.rabbit_user,
        settings.rabbit_password,
        rabbit_settings=settings.rabbit_publisher,
    )

    w_render = Render(
        db,
        rabbit_consumer,
        rabbit_publisher,
    )

    email = EmailSMTP(
        address=settings.email_settings.address,
        port=settings.email_settings.port,
        login=settings.email_settings.login,
        password=settings.email_settings.password,
    )

    w_sender = Sender(db, rabbit_publisher, email)

    logger.info("run worker")
    while True:
        db.connect()
        rabbit_consumer.connect()
        rabbit_publisher.connect()
        email.connect()
        try:
            rabbit_consumer.listen_channel(w_render.callback, auto_ack=False)
            rabbit_publisher.listen_channel(w_sender.callback, auto_ack=False)
        except Exception as e:
            logger.error(e)
