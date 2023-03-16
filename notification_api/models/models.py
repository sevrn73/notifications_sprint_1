from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationType(Enum):
    NEW_SERIES = "new_series"
    EMAIL = "email_confirmation"
    RECOMMENDATIONS = "recommendations"


class FilmsData(BaseModel):
    film_id: UUID
    film_name: str


class Payload(BaseModel):
    films_data: Optional[List[FilmsData]]


class Context(BaseModel):
    users_id: Optional[List[UUID]]
    group_id: Optional[UUID]
    payload: Optional[Payload]
    link: Optional[str]


class NotificationsExt(BaseModel):
    type_send: str = Field(NotificationType.NEW_SERIES)
    template_id: UUID
    notification_id: Optional[UUID]
    last_chunk: bool = False
    context: Context
