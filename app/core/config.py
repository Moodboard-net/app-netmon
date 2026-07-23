import base64
import binascii
from functools import lru_cache
from typing import Literal

from pydantic import Field, ValidationError, field_validator
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

    @field_validator("credential_encryption_key")
    @classmethod
    def _validate_credential_encryption_key(cls, value: str) -> str:
        try:
            raw = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(
                "CREDENTIAL_ENCRYPTION_KEY harus berupa base64 yang valid "
                "(generate dengan `python -m app.cli generate-key`)"
            ) from exc
        if len(raw) != 32:
            raise ValueError(
                "CREDENTIAL_ENCRYPTION_KEY harus 32 byte (AES-256) setelah didekode base64, "
                f"didapat {len(raw)} byte"
            )
        return value

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
        parts = []
        for err in exc.errors():
            field = str(err["loc"][0])
            if err["type"] == "value_error":
                parts.append(f"{field} ({err['msg']})")
            else:
                parts.append(field)
        raise RuntimeError(
            "Konfigurasi tidak lengkap atau tidak valid. Variabel bermasalah: "
            f"{'; '.join(sorted(parts))}"
        ) from exc
