from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "mysql+aiomysql://hellio:hellio123@localhost:3306/hellio_hr"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-characters"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Hellio HR API"
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Storage
    STORAGE_PATH: str = "./storage/documents"

    # Ingestion / LLM
    INGESTION_PROVIDER: str = "bedrock"          # "bedrock" or "anthropic"
    INGESTION_MODEL: str = "amazon.nova-pro-v1:0"  # overridden per provider
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BEARER_TOKEN_BEDROCK: str = ""
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def allowed_origins_list(self) -> list[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
