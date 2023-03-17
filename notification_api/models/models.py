from enum import Enum
from typing import List, Optional
from uuid import UUID

import orjson
from pydantic import BaseModel as BaseModelPyd
from pydantic import Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonBaseModel(BaseModelPyd):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class NotificationType(Enum):
    NEW_SERIES = "new_series"
    EMAIL = "email_confirmation"
    RECOMMENDATIONS = "recommendations"


class FilmsData(OrjsonBaseModel):
    film_id: UUID
    film_name: str


class Payload(OrjsonBaseModel):
    films_data: Optional[List[FilmsData]]


class Context(OrjsonBaseModel):
    users_id: Optional[List[UUID]]
    group_id: Optional[UUID]
    payload: Optional[Payload]
    link: Optional[str]


class NotificationsExt(OrjsonBaseModel):
    type_send: str = Field(NotificationType.NEW_SERIES)
    template_id: UUID
    notification_id: Optional[UUID]
    last_chunk: bool = False
    context: Context
