from fastapi import APIRouter

from app.service.auth_service import build_local_jwk

router = APIRouter(tags=["well-known"])


@router.get("/.well-known/jwks.json")
async def get_jwks():
    return {"keys": [build_local_jwk()]}
