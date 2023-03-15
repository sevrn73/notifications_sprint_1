import http

import requests
from faker import Faker
from pydantic import BaseModel
from requests import Session


class User(BaseModel):
    user_id: str
    user_name: str
    user_email: str


class ApiUserInfo:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session: Session = None

    def connect(self):
        if not self.session:
            self.session = requests.Session()

    def get_user(self, uuid):
        url = f"{self.base_url}/user"
        data = {"user_id": uuid}
        result = self.session.post(url, data=data)
        if result.status_code != http.HTTPStatus.OK:
            raise ValueError(result)
        return User(**result)


fake = Faker()


class ApiUserInfoFake(ApiUserInfo):
    def get_user(self, uuid):
        return User(**{"user_id": uuid, "user_name": fake.name(), "user_email": fake.email()})
