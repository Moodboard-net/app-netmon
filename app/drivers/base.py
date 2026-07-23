from abc import ABC, abstractmethod
from typing import ClassVar, Self

from app.drivers.exceptions import CapabilityNotSupported
from app.models.device import Device
from app.schemas.credential import DecryptedCredential
from app.schemas.device_data import Facts, FirewallRule, InterfaceCounter, InterfaceInfo, NeighborInfo, Route, Vlan

CAPABILITY_FACTS = "facts"
CAPABILITY_INTERFACES = "interfaces"
CAPABILITY_COUNTERS = "counters"
CAPABILITY_VLANS = "vlans"
CAPABILITY_NEIGHBORS = "neighbors"
CAPABILITY_ROUTING_TABLE = "routing_table"
CAPABILITY_FIREWALL_RULES = "firewall_rules"


class BaseDriver(ABC):
    """Kontrak seragam untuk mengambil data dari perangkat multi-vendor.

    Subclass mengimplementasikan method berawalan underscore (mis. `_get_facts`)
    dengan logika spesifik vendor. Method publik (`get_facts`, dst.) menegakkan
    guard capability secara terpusat, jadi driver baru tidak bisa lupa
    menerapkannya.
    """

    capabilities: ClassVar[frozenset[str]] = frozenset()

    def __init__(self, *, device: Device, credential: DecryptedCredential) -> None:
        self.device = device
        self.credential = credential
        self.os_variant: str | None = None
        self.detected_capabilities: frozenset[str] = frozenset()

    async def __aenter__(self) -> Self:
        await self._connect()
        self.os_variant = await self._detect_os_variant()
        self.detected_capabilities = await self._detect_capabilities()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self._disconnect()

    def _require_capability(self, capability: str) -> None:
        if capability not in self.capabilities:
            raise CapabilityNotSupported(
                f"{type(self).__name__} tidak mendukung capability '{capability}'"
            )

    @abstractmethod
    async def _connect(self) -> None: ...

    @abstractmethod
    async def _disconnect(self) -> None: ...

    @abstractmethod
    async def _detect_os_variant(self) -> str: ...

    async def _detect_capabilities(self) -> frozenset[str]:
        """Default: anggap semua capability kandidat kelas ini didukung.

        Override kalau driver perlu memeriksa kemampuan aktual perangkat
        (mis. fitur yang dimatikan di firmware tertentu).
        """
        return self.capabilities

    async def get_facts(self) -> Facts:
        self._require_capability(CAPABILITY_FACTS)
        return await self._get_facts()

    @abstractmethod
    async def _get_facts(self) -> Facts: ...

    async def get_interfaces(self) -> list[InterfaceInfo]:
        self._require_capability(CAPABILITY_INTERFACES)
        return await self._get_interfaces()

    @abstractmethod
    async def _get_interfaces(self) -> list[InterfaceInfo]: ...

    async def get_interface_counters(self) -> list[InterfaceCounter]:
        self._require_capability(CAPABILITY_COUNTERS)
        return await self._get_interface_counters()

    @abstractmethod
    async def _get_interface_counters(self) -> list[InterfaceCounter]: ...

    async def get_vlans(self) -> list[Vlan]:
        self._require_capability(CAPABILITY_VLANS)
        return await self._get_vlans()

    @abstractmethod
    async def _get_vlans(self) -> list[Vlan]: ...

    async def get_neighbors(self) -> list[NeighborInfo]:
        self._require_capability(CAPABILITY_NEIGHBORS)
        return await self._get_neighbors()

    @abstractmethod
    async def _get_neighbors(self) -> list[NeighborInfo]: ...

    async def get_routing_table(self) -> list[Route]:
        self._require_capability(CAPABILITY_ROUTING_TABLE)
        return await self._get_routing_table()

    @abstractmethod
    async def _get_routing_table(self) -> list[Route]: ...

    async def get_firewall_rules(self) -> list[FirewallRule]:
        self._require_capability(CAPABILITY_FIREWALL_RULES)
        return await self._get_firewall_rules()

    @abstractmethod
    async def _get_firewall_rules(self) -> list[FirewallRule]: ...
