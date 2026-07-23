from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.drivers.base import BaseDriver
from app.models.device import Device, DeviceCapability
from app.models.reference import Capability


async def sync_detected_capabilities(session: AsyncSession, device: Device, driver: BaseDriver) -> None:
    device.os_variant = driver.os_variant

    capability_ids_by_name = dict((await session.execute(select(Capability.name, Capability.id))).all())

    existing_capability_ids = set(
        (
            await session.execute(
                select(DeviceCapability.capability_id).where(DeviceCapability.device_id == device.id)
            )
        ).scalars()
    )

    for name in driver.detected_capabilities:
        capability_id = capability_ids_by_name.get(name)
        if capability_id is None or capability_id in existing_capability_ids:
            continue
        session.add(DeviceCapability(device_id=device.id, capability_id=capability_id))

    await session.flush()
