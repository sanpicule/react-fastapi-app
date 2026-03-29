from fastapi import APIRouter

from app.api import jwks
from app.api.v1 import audit_logs, auth, users

router = APIRouter()

router.include_router(jwks.router)

# API v1
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth.router)
api_v1.include_router(users.router)
api_v1.include_router(audit_logs.router)

router.include_router(api_v1)
