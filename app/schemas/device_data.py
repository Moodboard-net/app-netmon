from pydantic import BaseModel


class Facts(BaseModel):
    hostname: str
    model: str | None = None
    os_version: str | None = None
    uptime_seconds: int | None = None
    serial_number: str | None = None


class InterfaceInfo(BaseModel):
    name: str
    alias: str | None = None
    interface_type: str | None = None
    mac_address: str | None = None
    speed_mbps: int | None = None
    admin_status: str | None = None
    oper_status: str | None = None


class InterfaceCounter(BaseModel):
    interface_name: str
    octets_in: int
    octets_out: int
    errors_in: int
    errors_out: int
    discards_in: int
    discards_out: int


class Vlan(BaseModel):
    vlan_id: int
    name: str | None = None


class NeighborInfo(BaseModel):
    protocol: str
    local_interface: str | None = None
    remote_hostname: str | None = None
    remote_port: str | None = None
    remote_mgmt_address: str | None = None
    remote_platform: str | None = None


class Route(BaseModel):
    destination: str
    next_hop: str | None = None
    interface: str | None = None
    metric: int | None = None
    protocol: str | None = None


class FirewallRule(BaseModel):
    chain: str
    action: str
    protocol: str | None = None
    source: str | None = None
    destination: str | None = None
    position: int | None = None
