from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, PkMixin, TimestampMixin


class Vendor(Base, PkMixin, TimestampMixin):
    __tablename__ = "vendors"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    driver_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class DeviceType(Base, PkMixin, TimestampMixin):
    __tablename__ = "device_types"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class Capability(Base, PkMixin, TimestampMixin):
    __tablename__ = "capabilities"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
