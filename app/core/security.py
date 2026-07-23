import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings

NONCE_SIZE = 12


def generate_master_key() -> str:
    return base64.b64encode(AESGCM.generate_key(bit_length=256)).decode("ascii")


def _load_key() -> bytes:
    return base64.b64decode(get_settings().credential_encryption_key)


def encrypt_secret(plaintext: bytes) -> bytes:
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(_load_key()).encrypt(nonce, plaintext, associated_data=None)
    return nonce + ciphertext


def decrypt_secret(blob: bytes) -> bytes:
    if get_settings().process_role != "worker":
        raise PermissionError(
            "decrypt_secret hanya boleh dipanggil dari proses worker (PROCESS_ROLE=worker), "
            f"bukan dari '{get_settings().process_role}'"
        )
    nonce, ciphertext = blob[:NONCE_SIZE], blob[NONCE_SIZE:]
    return AESGCM(_load_key()).decrypt(nonce, ciphertext, associated_data=None)
