from typing import Optional

import orjson
from pydantic import BaseModel as BaseModelPyd
from pydantic import Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonBaseModel(BaseModelPyd):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Context(OrjsonBaseModel):
    users_id: Optional[list] = Field(None)
    group_id: Optional[str] = Field(None)
    payload: Optional[dict] = Field({})


class Message(OrjsonBaseModel):
    type_send: str
    notification_id: str
    template_id: str
    context: Context


class NotificationStatus:
    WAITING = "waiting"
    PROCESSING = "processing"
    DONE = "done"
