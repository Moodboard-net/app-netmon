import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings

REQUIRED_ENV = {
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "test",
    "POSTGRES_PASSWORD": "test",
    "POSTGRES_DB": "test",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
}


def _set_required_env(monkeypatch, tmp_path):
    # Isolasi dari .env asli proyek: pindah ke direktori kosong supaya
    # Settings hanya membaca dari environment variable yang di-set eksplisit.
    monkeypatch.chdir(tmp_path)
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)


def test_settings_raises_when_required_var_missing(monkeypatch, tmp_path):
    _set_required_env(monkeypatch, tmp_path)
    monkeypatch.delenv("POSTGRES_PASSWORD")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_succeeds_when_all_required_vars_present(monkeypatch, tmp_path):
    _set_required_env(monkeypatch, tmp_path)

    settings = Settings()

    assert settings.postgres_host == "localhost"
    assert settings.redis_host == "localhost"


def test_get_settings_fails_fast_with_clear_message(monkeypatch, tmp_path):
    _set_required_env(monkeypatch, tmp_path)
    monkeypatch.delenv("POSTGRES_PASSWORD")
    get_settings.cache_clear()

    with pytest.raises(RuntimeError, match="postgres_password"):
        get_settings()


def test_settings_rejects_non_base64_encryption_key(monkeypatch, tmp_path):
    _set_required_env(monkeypatch, tmp_path)
    monkeypatch.setenv("CREDENTIAL_ENCRYPTION_KEY", "not-valid-base64!!!")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_rejects_encryption_key_with_wrong_length(monkeypatch, tmp_path):
    import base64

    _set_required_env(monkeypatch, tmp_path)
    # 16 byte (AES-128), bukan 32 byte (AES-256) yang dibutuhkan.
    monkeypatch.setenv("CREDENTIAL_ENCRYPTION_KEY", base64.b64encode(b"0" * 16).decode())

    with pytest.raises(ValidationError):
        Settings()


def test_get_settings_fails_fast_with_clear_message_on_bad_encryption_key(monkeypatch, tmp_path):
    _set_required_env(monkeypatch, tmp_path)
    monkeypatch.setenv("CREDENTIAL_ENCRYPTION_KEY", "not-valid-base64!!!")
    get_settings.cache_clear()

    with pytest.raises(RuntimeError, match="credential_encryption_key"):
        get_settings()
