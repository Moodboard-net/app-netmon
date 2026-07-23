from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import decrypt_secret, encrypt_secret
from app.models.device import DeviceCredential
from app.schemas.credential import DecryptedCredential


async def save_credential(
    session: AsyncSession,
    *,
    device_id: int,
    auth_method: str,
    secret: bytes,
    username: str | None = None,
) -> DeviceCredential:
    result = await session.execute(select(DeviceCredential).where(DeviceCredential.device_id == device_id))
    credential = result.scalar_one_or_none()

    if credential is None:
        credential = DeviceCredential(device_id=device_id)
        session.add(credential)

    credential.auth_method = auth_method
    credential.username = username
    credential.secret_ciphertext = encrypt_secret(secret)
    credential.encryption_key_id = get_settings().credential_encryption_key_id

    await session.flush()
    return credential


async def get_credential(session: AsyncSession, *, device_id: int) -> DecryptedCredential:
    result = await session.execute(select(DeviceCredential).where(DeviceCredential.device_id == device_id))
    credential = result.scalar_one()

    # Rotasi master key belum didukung: hanya satu key aktif yang bisa mendekripsi.
    # Kalau key sudah dirotasi tapi baris ini masih pakai key_id lama, gagal di sini
    # dengan pesan jelas -- daripada diam-diam gagal dengan GCM auth-tag error yang
    # membingungkan di decrypt_secret().
    current_key_id = get_settings().credential_encryption_key_id
    if credential.encryption_key_id != current_key_id:
        raise RuntimeError(
            f"Kredensial device_id={device_id} dienkripsi dengan encryption_key_id="
            f"'{credential.encryption_key_id}', tapi CREDENTIAL_ENCRYPTION_KEY_ID saat ini "
            f"adalah '{current_key_id}'. Rotasi master key belum didukung otomatis -- "
            "key lama harus tetap dipakai untuk mendekripsi kredensial ini."
        )

    plaintext = decrypt_secret(credential.secret_ciphertext)

    return DecryptedCredential(
        device_id=credential.device_id,
        auth_method=credential.auth_method,
        username=credential.username,
        secret=plaintext,
    )
