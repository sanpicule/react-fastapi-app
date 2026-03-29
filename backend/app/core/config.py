from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    auth_issuer: str = "http://localhost:8000"
    auth_audience: str = "my-monolith"
    auth_jwks_url: str = "http://localhost:8000/.well-known/jwks.json"
    auth_algorithm: str = "RS256"
    auth_access_token_ttl_minutes: int = 60
    auth_jwks_cache_ttl_seconds: int = 300
    auth_local_private_key_path: str = ".local-auth/private.pem"
    auth_local_public_key_path: str = ".local-auth/public.pem"
    auth_local_key_id: str = "local-dev-key-1"
    auth_dev_login_email: str = "admin@example.com"
    auth_dev_login_password: str = "dev-password"
    auth_dev_login_name: str = "Local Admin"
    auth_dev_login_user_id: int = 1
    auth_dev_login_roles: str = "admin"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


# インスタンスを作成して利用可能にする
settings = Settings()  # type: ignore
