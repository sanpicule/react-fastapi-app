from fastapi import APIRouter
from app.api.v1 import users, audit_logs

router = APIRouter()

# API v1
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(users.router)
api_v1.include_router(audit_logs.router)

router.include_router(api_v1)
