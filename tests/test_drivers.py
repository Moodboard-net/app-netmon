import pytest

from app.drivers.base import CAPABILITY_FACTS, CAPABILITY_INTERFACES, BaseDriver
from app.drivers.exceptions import CapabilityNotSupported
from app.drivers.registry import get_driver, get_driver_class, register_driver
from app.models.device import Device
from app.models.reference import Vendor
from app.schemas.credential import DecryptedCredential
from app.schemas.device_data import (
    Facts,
    FirewallRule,
    InterfaceCounter,
    InterfaceInfo,
    NeighborInfo,
    Route,
    Vlan,
)


class FakeDriver(BaseDriver):
    capabilities = frozenset({CAPABILITY_FACTS, CAPABILITY_INTERFACES})

    def __init__(self, *, device, credential):
        super().__init__(device=device, credential=credential)
        self.connected = False
        self.disconnected = False

    async def _connect(self) -> None:
        self.connected = True

    async def _disconnect(self) -> None:
        self.disconnected = True

    async def _detect_os_variant(self) -> str:
        return "fake_v1"

    async def _get_facts(self) -> Facts:
        return Facts(hostname="fake-host", model="FakeModel", os_version="1.0", uptime_seconds=100)

    async def _get_interfaces(self) -> list[InterfaceInfo]:
        return [InterfaceInfo(name="eth0", admin_status="up", oper_status="up")]

    async def _get_interface_counters(self) -> list[InterfaceCounter]:
        raise NotImplementedError

    async def _get_vlans(self) -> list[Vlan]:
        raise NotImplementedError

    async def _get_neighbors(self) -> list[NeighborInfo]:
        raise NotImplementedError

    async def _get_routing_table(self) -> list[Route]:
        raise NotImplementedError

    async def _get_firewall_rules(self) -> list[FirewallRule]:
        raise NotImplementedError


def _make_device_and_credential() -> tuple[Device, DecryptedCredential]:
    device = Device(id=1, name="fake-device", management_ip="10.0.0.1", vendor_id=1, device_type_id=1)
    device.vendor = Vendor(id=1, name="fakevendor", driver_key="fakevendor-test")
    credential = DecryptedCredential(device_id=1, auth_method="password", username="admin", secret=b"pw")
    return device, credential


@pytest.mark.anyio
async def test_supported_capability_returns_uniform_schema():
    device, credential = _make_device_and_credential()
    driver = FakeDriver(device=device, credential=credential)

    async with driver:
        facts = await driver.get_facts()
        interfaces = await driver.get_interfaces()

    assert isinstance(facts, Facts)
    assert facts.hostname == "fake-host"
    assert isinstance(interfaces, list)
    assert isinstance(interfaces[0], InterfaceInfo)


@pytest.mark.anyio
async def test_unsupported_capability_raises_capability_not_supported():
    device, credential = _make_device_and_credential()
    driver = FakeDriver(device=device, credential=credential)

    async with driver:
        with pytest.raises(CapabilityNotSupported):
            await driver.get_vlans()


@pytest.mark.anyio
async def test_context_manager_connects_and_detects_on_entry():
    device, credential = _make_device_and_credential()
    driver = FakeDriver(device=device, credential=credential)

    async with driver:
        assert driver.connected is True
        assert driver.os_variant == "fake_v1"
        assert driver.detected_capabilities == FakeDriver.capabilities


@pytest.mark.anyio
async def test_context_manager_disconnects_even_on_exception():
    device, credential = _make_device_and_credential()
    driver = FakeDriver(device=device, credential=credential)

    with pytest.raises(ValueError, match="boom"):
        async with driver:
            raise ValueError("boom")

    assert driver.disconnected is True


def test_get_driver_returns_registered_class_instance():
    register_driver("fakevendor-test")(FakeDriver)
    device, credential = _make_device_and_credential()

    driver = get_driver(device, credential)

    assert isinstance(driver, FakeDriver)
    assert driver.device is device
    assert driver.credential is credential


def test_get_driver_class_raises_clear_error_for_unknown_key():
    with pytest.raises(ValueError, match="unknown-vendor-xyz"):
        get_driver_class("unknown-vendor-xyz")
