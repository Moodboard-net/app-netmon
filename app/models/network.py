from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import INET, MACADDR
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, PkMixin, TimestampMixin


class Interface(Base, PkMixin, TimestampMixin):
    __tablename__ = "interfaces"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    alias: Mapped[str | None] = mapped_column(String(255))
    interface_type: Mapped[str | None] = mapped_column(String(50))
    mac_address: Mapped[str | None] = mapped_column(MACADDR)
    speed_mbps: Mapped[int | None] = mapped_column(BigInteger)
    admin_status: Mapped[str | None] = mapped_column(String(20))
    oper_status: Mapped[str | None] = mapped_column(String(20))

    __table_args__ = (
        UniqueConstraint("device_id", "name", name="uq_interfaces_device_name"),
        Index("ix_interfaces_device_id", "device_id"),
    )


class InterfaceMetric(Base, TimestampMixin):
    """Partisi RANGE bulanan berdasarkan recorded_at; lihat app/services/partitioning.py."""

    __tablename__ = "interface_metrics"
    __table_args__ = (
        Index("ix_interface_metrics_interface_id", "interface_id"),
        Index("ix_interface_metrics_recorded_at", "recorded_at"),
        {"postgresql_partition_by": "RANGE (recorded_at)"},
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, nullable=False)
    interface_id: Mapped[int] = mapped_column(ForeignKey("interfaces.id", ondelete="CASCADE"), nullable=False)
    octets_in: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    octets_out: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    errors_in: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    errors_out: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    discards_in: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    discards_out: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")


class Neighbor(Base, PkMixin, TimestampMixin):
    __tablename__ = "neighbors"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    local_interface_id: Mapped[int | None] = mapped_column(
        ForeignKey("interfaces.id", ondelete="SET NULL")
    )
    protocol: Mapped[str] = mapped_column(String(20), nullable=False)
    remote_hostname: Mapped[str | None] = mapped_column(String(255))
    remote_port: Mapped[str | None] = mapped_column(String(255))
    remote_mgmt_address: Mapped[str | None] = mapped_column(INET)
    remote_platform: Mapped[str | None] = mapped_column(String(255))
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_neighbors_device_id", "device_id"),
        Index("ix_neighbors_local_interface_id", "local_interface_id"),
    )
