import logging
from datetime import datetime
from typing import List

import backoff
import psycopg2
from config import BACKOFF_CONFIG, Settings
from psycopg2.extras import RealDictCursor, RealDictRow
from utils.models import NotificationStatus

db_logger = logging.getLogger(__name__)

BACKOFF_CONFIG.update({"logger": db_logger})


class PGConnectorBase:
    """
    Базовый интерфейс для работы с postgress
    """

    def __init__(self, settings: Settings):
        """
        Parameters
        ----------
        :param settings: настройки проекта
        -------
        """
        self.settings = settings
        self.db = None
        self.cursor = None
        self.connect()

    @backoff.on_exception(**BACKOFF_CONFIG)
    def connect(self) -> None:
        """
        Установка соединения с postgress
        """
        self.db = psycopg2.connect(
            host=self.settings.PG_HOST,
            port=self.settings.PG_PORT,
            user=self.settings.PG_USER,
            password=self.settings.PG_PASSWORD,
            dbname=self.settings.DB_NAME,
            cursor_factory=RealDictCursor,
        )
        self.cursor = self.db.cursor()
        db_logger.info("connect db")

    @backoff.on_exception(**BACKOFF_CONFIG)
    def get_query(self, sql: str) -> List[RealDictRow]:
        """
        Получение данных из postgress

        Parameters
        ----------
        :param sql: SQL-запрос
        -------
        """
        try:
            self.cursor.execute(sql)
        except psycopg2.OperationalError:
            db_logger.info("Postgres connection error")
            self.connect()
            self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    @backoff.on_exception(**BACKOFF_CONFIG)
    def set_query(self, sql: str):
        """
        Отправка данных в postgress

        Parameters
        ----------
        :param sql: SQL-запрос
        -------
        """
        try:
            self.cursor.execute(sql)
        except psycopg2.OperationalError:
            db_logger.info("Postgres connection error")
            self.connect()
            self.cursor.execute(sql)
        self.db.commit()

    def close(self) -> None:
        """
        Закрытие соединения с postgress
        """
        if self.db:
            self.db.close()


class PGNotification(PGConnectorBase):
    def get_notification(self):
        """
        Получение ожидающих отправки нотификаций из postgress
        """
        sql_tmp = (
            "select notification.id, context.template_id as template_id, context.params, type.title "
            "from notification_notification notification "
            "left join notification_context context on context.id = notification.context_id "
            "left join notification_template template on context.template_id = template.id "
            "left join notification_notificationtype type on type.id = template.notification_type_id "
            "WHERE notification.send_date <= %(timestamp)s and send_status = %(notification_status)s"
        )
        sql = self.cursor.mogrify(
            sql_tmp,
            {"timestamp": datetime.now(), "notification_status": NotificationStatus.WAITING},
        )
        db_logger.debug(sql)
        result = self.get_query(sql)
        db_logger.debug(result)
        return result

    def set_status_processing(self, notification_id):
        """
        Обновление статуса нотификации в postgress

        Parameters
        ----------
        :param notification_id: id нотификации
        -------
        """
        sql_tmp = (
            "UPDATE notification_notification "
            "SET send_status=%(status)s "
            "WHERE id = %(notification_id)s"
        )
        sql = self.cursor.mogrify(
            sql_tmp,
            {"status": NotificationStatus.PROCESSING, "notification_id": notification_id},
        )
        self.set_query(sql)
