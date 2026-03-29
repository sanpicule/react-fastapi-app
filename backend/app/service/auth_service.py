from __future__ import annotations

import hmac
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from jose import jwt
from jose.utils import base64url_encode

from app.core.config import settings

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class InvalidCredentialsError(Exception):
    pass


def _resolve_backend_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return BACKEND_ROOT / path


def _int_to_bytes(value: int) -> bytes:
    length = max(1, (value.bit_length() + 7) // 8)
    return value.to_bytes(length, "big")


def get_dev_login_roles() -> list[str]:
    return [role.strip() for role in settings.auth_dev_login_roles.split(",") if role.strip()]


def get_dev_login_user() -> dict[str, object]:
    return {
        "user_id": settings.auth_dev_login_user_id,
        "subject": str(settings.auth_dev_login_user_id),
        "email": settings.auth_dev_login_email,
        "name": settings.auth_dev_login_name,
        "roles": get_dev_login_roles(),
    }


def ensure_local_rsa_key_pair() -> None:
    private_key_path = _resolve_backend_path(settings.auth_local_private_key_path)
    public_key_path = _resolve_backend_path(settings.auth_local_public_key_path)

    if private_key_path.exists() and public_key_path.exists():
        return

    private_key_path.parent.mkdir(parents=True, exist_ok=True)
    public_key_path.parent.mkdir(parents=True, exist_ok=True)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_key_path.write_bytes(private_pem)
    public_key_path.write_bytes(public_pem)


def load_local_private_key_pem() -> str:
    ensure_local_rsa_key_pair()
    return _resolve_backend_path(settings.auth_local_private_key_path).read_text()


def load_local_public_key_pem() -> str:
    ensure_local_rsa_key_pair()
    return _resolve_backend_path(settings.auth_local_public_key_path).read_text()


def build_local_jwk() -> dict[str, str]:
    public_key = load_pem_public_key(load_local_public_key_pem().encode("utf-8"))
    public_numbers = public_key.public_numbers()

    return {
        "kty": "RSA",
        "kid": settings.auth_local_key_id,
        "use": "sig",
        "alg": settings.auth_algorithm,
        "n": base64url_encode(_int_to_bytes(public_numbers.n)).decode("utf-8"),
        "e": base64url_encode(_int_to_bytes(public_numbers.e)).decode("utf-8"),
    }


def authenticate_dev_user(email: str, password: str) -> dict[str, object]:
    expected_email = settings.auth_dev_login_email.strip().lower()
    if email.strip().lower() != expected_email:
        raise InvalidCredentialsError("メールアドレスまたはパスワードが正しくありません")

    if not hmac.compare_digest(password, settings.auth_dev_login_password):
        raise InvalidCredentialsError("メールアドレスまたはパスワードが正しくありません")

    return get_dev_login_user()


def issue_access_token(user: dict[str, object]) -> tuple[str, int]:
    ensure_local_rsa_key_pair()

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.auth_access_token_ttl_minutes)

    payload = {
        "sub": user["subject"],
        "user_id": user["user_id"],
        "email": user["email"],
        "name": user["name"],
        "roles": user["roles"],
        "iss": settings.auth_issuer,
        "aud": settings.auth_audience,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    headers = {
        "kid": settings.auth_local_key_id,
        "typ": "JWT",
    }

    token = jwt.encode(
        payload,
        load_local_private_key_pem(),
        algorithm=settings.auth_algorithm,
        headers=headers,
    )
    return token, int((expires_at - now).total_seconds())
