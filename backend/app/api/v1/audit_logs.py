from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas.audit_log import AuditLog, AuditLogListResponse
from app.service.audit_log_service import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("/", response_model=AuditLogListResponse)
async def get_audit_logs(
    limit: int = Query(15, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    service = AuditLogService(db)
    items = await service.get_audit_logs(limit=limit, offset=offset)
    total = await service.get_count()
    return AuditLogListResponse(items=items, total=total)
