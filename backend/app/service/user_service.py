
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.users import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def get_users(self) -> list[User]:
        return await self.repo.all()
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.repo.find_by_id(user_id)
