from pydantic import BaseModel, SecretBytes


class DecryptedCredential(BaseModel):
    device_id: int
    auth_method: str
    username: str | None
    secret: SecretBytes
