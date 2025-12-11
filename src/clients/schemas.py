from datetime import datetime

from pydantic import BaseModel


class ExternalCustomer(BaseModel):
    id: int
    createdAt: datetime
    lastName: str | None = None
    firstName: str | None = None
    email: str | None = None
    phones: list[dict[str, str]]
