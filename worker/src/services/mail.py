import logging
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage

import backoff

logger = logging.getLogger(__name__)


class SenderAbstraction(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def send(self, subject: str, address: str, message: str):
        pass

    @abstractmethod
    def close(self):
        pass


class EmailSMTP(SenderAbstraction):
    def __init__(self, address: str, port: int, login: str, password: str):
        self.address = address
        self.port = port
        self.login = login
        self.password = password
        self.server = None

    @backoff.on_exception(backoff.expo, Exception)
    def connect(self):
        if self.server is None:
            self.server = smtplib.SMTP_SSL(self.address, self.port)
            self.server.login(self.login, self.password)

    def send(self, subject: str, to_email: str, text: str):
        self.connect()

        message = EmailMessage()
        message["From"] = self.login
        message["To"] = to_email
        message["Subject"] = subject
        message.add_alternative(text, subtype="html")
        self.server.sendmail(self.login, to_email, message.as_string())

    def close(self):
        if self.server is not None:
            self.server.close()
