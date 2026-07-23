from datetime import date

INTERFACE_METRICS_TABLE = "interface_metrics"


def partition_name(table: str, year: int, month: int) -> str:
    return f"{table}_{year:04d}_{month:02d}"


def month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def create_partition_sql(table: str, year: int, month: int) -> str:
    name = partition_name(table, year, month)
    start, end = month_bounds(year, month)
    return (
        f'CREATE TABLE IF NOT EXISTS "{name}" '
        f'PARTITION OF "{table}" FOR VALUES FROM (\'{start.isoformat()}\') TO (\'{end.isoformat()}\')'
    )
