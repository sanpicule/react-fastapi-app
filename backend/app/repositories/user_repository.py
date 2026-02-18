from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def all(self) -> list[User]:
        result = await self.db.execute(select(User))
        return list(result.scalars().all())
    
    async def find_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
