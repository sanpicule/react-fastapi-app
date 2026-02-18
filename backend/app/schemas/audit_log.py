from datetime import datetime
from pydantic import BaseModel


class AuditLog(BaseModel):
    id: int
    user_id: int | None
    action: str
    resource_type: str | None
    resource_id: int | None
    details: str | None
    request_body: str | None
    response_body: str | None
    ip_address: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    items: list[AuditLog]
    total: int
