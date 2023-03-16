from typing import Optional, List

from pydantic import BaseModel


class MessageBase(BaseModel):
    type_send: str
    template_id: str
    last_chunk: bool = False
    notification_id: Optional[str]


class FilmData(BaseModel):
    film_id: str
    film_name: str


class Payload(BaseModel):
    films_data: Optional[List[FilmData]]
    link: Optional[str]


class Context(BaseModel):
    users_id: list
    payload: Payload


class Message(MessageBase):
    context: Context


class ContextChunk(BaseModel):
    users_id: Optional[list]
    group_id: Optional[str]
    payload: dict


class MessageChunk(MessageBase):
    context: ContextChunk
