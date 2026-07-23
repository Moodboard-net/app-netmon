from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Identity, Index, Integer, LargeBinary, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, PkMixin, TimestampMixin
from app.models.reference import DeviceType, Vendor


class Device(Base, PkMixin, TimestampMixin):
    __tablename__ = "devices"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    management_ip: Mapped[str] = mapped_column(INET, nullable=False)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id", ondelete="RESTRICT"), nullable=False)
    device_type_id: Mapped[int] = mapped_column(
        ForeignKey("device_types.id", ondelete="RESTRICT"), nullable=False
    )
    model: Mapped[str | None] = mapped_column(String(100))
    os_version: Mapped[str | None] = mapped_column(String(100))
    os_variant: Mapped[str | None] = mapped_column(String(50))
    serial_number: Mapped[str | None] = mapped_column(String(100))
    site: Mapped[str | None] = mapped_column(String(100))
    poll_interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="300")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    raw_facts: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    vendor: Mapped["Vendor"] = relationship()
    device_type: Mapped["DeviceType"] = relationship()

    __table_args__ = (
        Index("ix_devices_vendor_id", "vendor_id"),
        Index("ix_devices_device_type_id", "device_type_id"),
        Index("ix_devices_management_ip", "management_ip"),
        Index("ix_devices_is_active", "is_active"),
        Index("ix_devices_raw_facts", "raw_facts", postgresql_using="gin"),
    )


class DeviceCredential(Base, PkMixin, TimestampMixin):
    __tablename__ = "device_credentials"

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    auth_method: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255))
    secret_ciphertext: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encryption_key_id: Mapped[str] = mapped_column(String(100), nullable=False)

    device: Mapped["Device"] = relationship()


class DeviceCapability(Base, TimestampMixin):
    __tablename__ = "device_capabilities"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    capability_id: Mapped[int] = mapped_column(
        ForeignKey("capabilities.id", ondelete="RESTRICT"), nullable=False
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("device_id", "capability_id", name="uq_device_capabilities_device_capability"),
        Index("ix_device_capabilities_device_id", "device_id"),
        Index("ix_device_capabilities_capability_id", "capability_id"),
    )
