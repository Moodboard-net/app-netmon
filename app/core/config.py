from functools import lru_cache
from typing import Literal

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "NetMon"
    environment: str = "development"
    process_role: Literal["api", "worker"] = "api"

    postgres_host: str = Field(min_length=1)
    postgres_port: int
    postgres_user: str = Field(min_length=1)
    postgres_password: str = Field(min_length=1)
    postgres_db: str = Field(min_length=1)

    redis_host: str = Field(min_length=1)
    redis_port: int
    redis_db: int = 0

    credential_encryption_key: str = Field(min_length=1)
    credential_encryption_key_id: str = "v1"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        missing = ", ".join(sorted({str(err["loc"][0]) for err in exc.errors()}))
        raise RuntimeError(
            "Konfigurasi tidak lengkap. Variabel wajib berikut kosong atau tidak diset "
            f"di .env: {missing}"
        ) from exc
