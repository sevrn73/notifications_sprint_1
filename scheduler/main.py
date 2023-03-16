import logging
from http import HTTPStatus

from time import sleep

from config import settings
from utils.postgres_helper import PGNotification, db_logger
from utils.models import Context, Message
from utils.rabbitmq_helper import send_message_to_api, rabbit_logger


logger = logging.getLogger(__name__)


def main(db: PGNotification) -> None:
    """
    Основная функция формирования отложенных уведовлений

    Parameters
    ----------
    :param db: интерфейс базы данных
    """
    try:
        print("ин трай")
        result = db.get_notification()
        data = [{key: value for key, value in item.items()} for item in result]

        for notification in data:
            context = Context(**notification["params"])
            message = Message(
                type_send=notification["title"],
                context=context,
                template_id=notification["template_id"],
                notification_id=notification["id"],
            )
            logger.debug(message.dict())
            resp = send_message_to_api(message.dict())
            if resp.status_code == HTTPStatus.OK:
                db.set_status_processing(message.notification_id)

    except Exception as e:
        logger.error(e)


def init_logger(loggers_list: list) -> None:
    """
    Функция для инициализации уровня логирования

    Parameters
    ----------
    :param loggers_list: список логеров
    """
    for logger in loggers_list:
        logger.setLevel("ERROR")


if __name__ == "__main__":

    loggers_list = [
        rabbit_logger,
        db_logger,
        logger,
    ]
    init_logger(loggers_list)

    pg = PGNotification(settings)

    while True:
        print("ин вайл")
        main(pg)
        sleep(settings.RESTART_TIME)
