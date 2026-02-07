from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def all(self) -> list[User]:
        result = await self.db.execute(select(User))
        return list(result.scalars().all())
