import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends

from dependencies.config import Settings, get_settings
from models.models import NotificationsExt
from utils.rabbitmq_client import rabbitmq_client


router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/send_notification",)
async def send_notification(
    notification: NotificationsExt, settings: Settings = Depends(get_settings),
):
    """
    Отправка уведомления в очередь RebbitMQ

    Parameters
    ----------
    :param notification: контракт, содержащий исходные данные для постановки нотификации в очередь
    :param settings: настройки проекта
    """
    if (
        notification.type_send == notification.type_send.new_series
        or notification.type_send == notification.type_send.email_confirmation
    ):
        logger.info(f"Принята нотификация для очереди {settings.email_queue}")
        notification.last_chunk = True
        await rabbitmq_client.send_rabbitmq(notification.dict(), settings.email_queue)
    else:
        logger.info(f"Принята нотификация для очереди {settings.group_queue}")
        await rabbitmq_client.send_rabbitmq(notification.dict(), settings.group_queue)
    return HTTPStatus.OK
