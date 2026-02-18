from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.audit_log import AuditLog


class AuditLogService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditLogRepository(db)

    async def get_audit_logs(self, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        return await self.repo.all(limit=limit, offset=offset)
    
    async def get_count(self) -> int:
        return await self.repo.count()
