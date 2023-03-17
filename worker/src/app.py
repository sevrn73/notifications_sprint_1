import logging
import threading
from typing import Any

from core.config import settings
from services.db import NotificationsDb
from services.mail import EmailSMTP
from services.rabbit import Rabbit, RabbitConsumer, RabbitPublisher
from services.render import Render
from services.sender import Sender

logger = logging.getLogger(__name__)


class ConsumerThread(threading.Thread):
    def __init__(self, host: str, rabbit_thread: Rabbit, callback_func: Any, *args, **kwargs):
        super(ConsumerThread, self).__init__(*args, **kwargs)

        self._host: str = host
        self.rabbit_thread: Rabbit = rabbit_thread
        self.callback_func: Any = callback_func

    def run(self):
        self.rabbit_thread.connect()
        # while True:
        try:
            self.rabbit_thread.listen_channel(self.callback_func, auto_ack=False)
        except Exception as e:
            logger.error(e)


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
    db.connect()
    # email.connect()
    threads = [
        ConsumerThread("host1", rabbit_consumer, w_render.callback),
        ConsumerThread("host2", rabbit_publisher, w_sender.callback),
    ]
    for thread in threads:
        thread.start()
