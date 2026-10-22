from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Prism Engine"
    app_version: str = "1.0.0"
    debug: bool = False
    demo_mode: bool = False

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Database
    database_url: str = "sqlite:///./prism.db"

    # Security
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OIDC/Keycloak
    oidc_enabled: bool = True
    oidc_issuer_url: str = "http://localhost:8080/realms/prism-engine"
    oidc_client_id: str = "prism-engine"
    oidc_client_secret: str = ""
    oidc_redirect_uri: str = "http://localhost:3000/auth/callback"
    oidc_scopes: str = "openid profile email roles"
    oidc_audience: str = "prism-engine"

    # Demo mode OIDC (local only)
    demo_oidc_issuer_url: str = "http://localhost:8080/realms/prism-engine"
    demo_oidc_client_id: str = "prism-engine-demo"
    demo_oidc_client_secret: str = "demo-secret"
    demo_oidc_redirect_uri: str = "http://localhost:3000/auth/callback"

    # LLM Providers
    llm_api_key: Optional[str] = None
    llm_provider: str = "openai-compatible"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: Optional[str] = None
    llm_timeout: float = 30.0

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Keycloak Admin (for realm management)
    keycloak_admin_user: str = "admin"
    keycloak_admin_password: str = "admin"
    keycloak_admin_url: str = "http://localhost:8080/admin"

    @property
    def effective_oidc_issuer_url(self) -> str:
        if self.demo_mode:
            return self.demo_oidc_issuer_url
        return self.oidc_issuer_url

    @property
    def effective_oidc_client_id(self) -> str:
        if self.demo_mode:
            return self.demo_oidc_client_id
        return self.oidc_client_id

    @property
    def effective_oidc_client_secret(self) -> str:
        if self.demo_mode:
            return self.demo_oidc_client_secret
        return self.oidc_client_secret

    @property
    def effective_oidc_redirect_uri(self) -> str:
        if self.demo_mode:
            return self.demo_oidc_redirect_uri
        return self.oidc_redirect_uri


@lru_cache()
def get_settings() -> Settings:
    import os
    in_test = os.environ.get("PYTEST_CURRENT_TEST") is not None
    settings = Settings()
    if not settings.demo_mode and not in_test and settings.secret_key == "dev-secret-change-in-production":
        raise ValueError("SECRET_KEY must be set in production (demo_mode=false)")
    if not settings.demo_mode and not in_test and not settings.oidc_client_secret:
        raise ValueError("OIDC_CLIENT_SECRET must be set in production (demo_mode=false)")
    return settings