"""seed reference data

Revision ID: 43b4c9084046
Revises: 650ea4a2ebd5
Create Date: 2026-07-23 04:29:56.343252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43b4c9084046'
down_revision: Union[str, None] = '650ea4a2ebd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

VENDORS = [
    {"name": "mikrotik", "driver_key": "mikrotik"},
    {"name": "cisco", "driver_key": "cisco"},
    {"name": "ruijie", "driver_key": "ruijie"},
]

DEVICE_TYPES = [
    {"name": "router"},
    {"name": "switch"},
    {"name": "firewall"},
    {"name": "access_point"},
]

CAPABILITIES = [
    {"name": "facts"},
    {"name": "interfaces"},
    {"name": "counters"},
    {"name": "vlans"},
    {"name": "neighbors"},
    {"name": "routing_table"},
    {"name": "firewall_rules"},
]


def upgrade() -> None:
    vendors = sa.table("vendors", sa.column("name", sa.String), sa.column("driver_key", sa.String))
    device_types = sa.table("device_types", sa.column("name", sa.String))
    capabilities = sa.table("capabilities", sa.column("name", sa.String))

    op.bulk_insert(vendors, VENDORS)
    op.bulk_insert(device_types, DEVICE_TYPES)
    op.bulk_insert(capabilities, CAPABILITIES)


def downgrade() -> None:
    vendor_names = tuple(v["name"] for v in VENDORS)
    device_type_names = tuple(dt["name"] for dt in DEVICE_TYPES)
    capability_names = tuple(c["name"] for c in CAPABILITIES)

    op.execute(sa.text("DELETE FROM vendors WHERE name IN :names").bindparams(
        sa.bindparam("names", value=vendor_names, expanding=True)
    ))
    op.execute(sa.text("DELETE FROM device_types WHERE name IN :names").bindparams(
        sa.bindparam("names", value=device_type_names, expanding=True)
    ))
    op.execute(sa.text("DELETE FROM capabilities WHERE name IN :names").bindparams(
        sa.bindparam("names", value=capability_names, expanding=True)
    ))
