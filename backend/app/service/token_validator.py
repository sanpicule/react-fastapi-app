from __future__ import annotations

import asyncio
import base64
import time
from typing import TypedDict

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

from app.core.config import settings


class AuthenticatedPrincipal(TypedDict):
    user_id: int
    subject: str
    email: str
    name: str
    roles: list[str]
    issuer: str


class TokenValidationError(Exception):
    pass


_jwks_cache: dict[str, object] | None = None
_jwks_cache_fetched_at = 0.0


def _decode_base64url(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


def _normalize_roles(raw_roles: object) -> list[str]:
    if raw_roles is None:
        return []
    if isinstance(raw_roles, str):
        return [raw_roles]
    if isinstance(raw_roles, list):
        return [str(role) for role in raw_roles if str(role).strip()]
    raise TokenValidationError("roles claim の形式が不正です")


def _coerce_user_id(user_id: object, subject: object) -> int:
    candidate = user_id if user_id is not None else subject
    try:
        return int(candidate)
    except (TypeError, ValueError) as exc:
        raise TokenValidationError("user_id を解決できません") from exc


def _fetch_jwks_sync() -> dict[str, object]:
    response = requests.get(settings.auth_jwks_url, timeout=5)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list):
        raise TokenValidationError("JWKS の形式が不正です")
    return payload


async def get_jwks(force_refresh: bool = False) -> dict[str, object]:
    global _jwks_cache, _jwks_cache_fetched_at

    cache_is_fresh = (
        _jwks_cache is not None
        and (time.monotonic() - _jwks_cache_fetched_at) < settings.auth_jwks_cache_ttl_seconds
    )
    if cache_is_fresh and not force_refresh:
        return _jwks_cache

    try:
        _jwks_cache = await asyncio.to_thread(_fetch_jwks_sync)
    except requests.RequestException as exc:
        raise TokenValidationError("JWKS を取得できませんでした") from exc

    _jwks_cache_fetched_at = time.monotonic()
    return _jwks_cache


def _find_jwk(keys: list[object], kid: str) -> dict[str, str] | None:
    for key in keys:
        if isinstance(key, dict) and key.get("kid") == kid:
            return {str(k): str(v) for k, v in key.items()}
    return None


def _jwk_to_public_pem(jwk_data: dict[str, str]) -> str:
    if jwk_data.get("kty") != "RSA":
        raise TokenValidationError("RSA 以外の JWK はサポートしていません")

    n_value = jwk_data.get("n")
    e_value = jwk_data.get("e")
    if not n_value or not e_value:
        raise TokenValidationError("JWK に必要な公開鍵情報がありません")

    public_numbers = rsa.RSAPublicNumbers(
        e=int.from_bytes(_decode_base64url(e_value), "big"),
        n=int.from_bytes(_decode_base64url(n_value), "big"),
    )
    public_key = public_numbers.public_key()

    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


async def validate_access_token(token: str) -> AuthenticatedPrincipal:
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise TokenValidationError("JWT ヘッダーを読み取れません") from exc

    kid = header.get("kid")
    if not kid:
        raise TokenValidationError("JWT ヘッダーに kid がありません")

    if header.get("alg") and header["alg"] != settings.auth_algorithm:
        raise TokenValidationError("JWT の署名アルゴリズムが不正です")

    jwks = await get_jwks()
    jwk_data = _find_jwk(jwks["keys"], kid)
    if jwk_data is None:
        jwks = await get_jwks(force_refresh=True)
        jwk_data = _find_jwk(jwks["keys"], kid)

    if jwk_data is None:
        raise TokenValidationError("JWT に対応する公開鍵が JWKS にありません")

    public_pem = _jwk_to_public_pem(jwk_data)

    try:
        payload = jwt.decode(
            token,
            public_pem,
            algorithms=[settings.auth_algorithm],
            audience=settings.auth_audience,
            issuer=settings.auth_issuer,
        )
    except ExpiredSignatureError as exc:
        raise TokenValidationError("トークンの有効期限が切れています") from exc
    except JWTClaimsError as exc:
        raise TokenValidationError("トークンの claim 検証に失敗しました") from exc
    except JWTError as exc:
        raise TokenValidationError("トークンの署名検証に失敗しました") from exc

    subject = payload.get("sub")
    email = payload.get("email")
    name = payload.get("name")
    if not isinstance(subject, str) or not subject.strip():
        raise TokenValidationError("sub claim がありません")
    if not isinstance(email, str) or not email.strip():
        raise TokenValidationError("email claim がありません")
    if not isinstance(name, str) or not name.strip():
        raise TokenValidationError("name claim がありません")

    return {
        "user_id": _coerce_user_id(payload.get("user_id"), subject),
        "subject": subject,
        "email": email,
        "name": name,
        "roles": _normalize_roles(payload.get("roles")),
        "issuer": str(payload.get("iss", "")),
    }
