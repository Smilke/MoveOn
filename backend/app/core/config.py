from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Meu Sistema"
    API_PREFIX: str = "/api"

    # Senhas
    DEFAULT_PATIENT_PASSWORD: str = "Senha124"
    DEFAULT_PHYSIO_PASSWORD: str = "Senha124"
    PASSWORD_RESET_TOKEN_MINUTES: int = 30

    # Email (SMTP)
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    SMTP_USE_TLS: bool = True
    EMAIL_FALLBACK_RETURN_TOKEN: bool = True

    # jeito novo de configurar no Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    DATABASE_URL: str = "sqlite:///./moveon_v5.db"

settings = Settings()