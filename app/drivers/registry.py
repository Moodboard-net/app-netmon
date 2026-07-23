from collections.abc import Callable

from app.drivers.base import BaseDriver
from app.models.device import Device
from app.schemas.credential import DecryptedCredential

_registry: dict[str, type[BaseDriver]] = {}


def register_driver(driver_key: str) -> Callable[[type[BaseDriver]], type[BaseDriver]]:
    def decorator(driver_cls: type[BaseDriver]) -> type[BaseDriver]:
        _registry[driver_key] = driver_cls
        return driver_cls

    return decorator


def get_driver_class(driver_key: str) -> type[BaseDriver]:
    try:
        return _registry[driver_key]
    except KeyError:
        raise ValueError(f"Tidak ada driver terdaftar untuk driver_key={driver_key!r}") from None


def get_driver(device: Device, credential: DecryptedCredential) -> BaseDriver:
    """Device.vendor harus sudah di-eager-load oleh pemanggil (mis. selectinload)."""
    driver_cls = get_driver_class(device.vendor.driver_key)
    return driver_cls(device=device, credential=credential)
