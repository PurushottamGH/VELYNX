from pydantic import BaseModel


class Source(BaseModel):
    url: str
    title: str | None = None
    snippet: str | None = None
    source: str | None = None
    score: float | None = None
