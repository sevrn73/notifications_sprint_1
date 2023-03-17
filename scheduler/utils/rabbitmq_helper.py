import json
import logging

import backoff
import requests

from config import BACKOFF_CONFIG, settings


rabbit_logger = logging.getLogger(__name__)

BACKOFF_CONFIG.update({"logger": rabbit_logger})


@backoff.on_exception(**BACKOFF_CONFIG)
def send_message_to_api(message: dict):
    """
    Обращение к notification_api

    Parameters
    ----------
    :param message: сообщение
    -------
    """
    rabbit_logger.info(f"Send message to notification API")
    resp = requests.post(settings.API_URL, data=json.dumps(message))
    return resp
