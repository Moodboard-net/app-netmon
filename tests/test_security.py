import base64

import pytest

from app.core.config import get_settings
from app.core.security import decrypt_secret, encrypt_secret, generate_master_key

REQUIRED_ENV = {
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "test",
    "POSTGRES_PASSWORD": "test",
    "POSTGRES_DB": "test",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
}


def _set_env(monkeypatch, tmp_path, **overrides):
    monkeypatch.chdir(tmp_path)
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("CREDENTIAL_ENCRYPTION_KEY", generate_master_key())
    for key, value in overrides.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()


def test_encrypt_decrypt_roundtrip(monkeypatch, tmp_path):
    _set_env(monkeypatch, tmp_path, PROCESS_ROLE="worker")

    ciphertext = encrypt_secret(b"super-secret-password")
    plaintext = decrypt_secret(ciphertext)

    assert plaintext == b"super-secret-password"


def test_nonce_is_random_each_time(monkeypatch, tmp_path):
    _set_env(monkeypatch, tmp_path, PROCESS_ROLE="worker")

    first = encrypt_secret(b"same-plaintext")
    second = encrypt_secret(b"same-plaintext")

    assert first != second


def test_decrypt_rejected_outside_worker(monkeypatch, tmp_path):
    _set_env(monkeypatch, tmp_path, PROCESS_ROLE="api")

    ciphertext = encrypt_secret(b"secret")

    with pytest.raises(PermissionError):
        decrypt_secret(ciphertext)


def test_master_key_missing_fails_fast(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("CREDENTIAL_ENCRYPTION_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(RuntimeError, match="credential_encryption_key"):
        get_settings()


def test_generate_master_key_produces_valid_aes256_key():
    raw = base64.b64decode(generate_master_key())

    assert len(raw) == 32
