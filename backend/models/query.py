from pydantic import BaseModel


class Query(BaseModel):
    text: str
    session_id: str | None = None
