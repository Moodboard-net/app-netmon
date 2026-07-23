from datetime import date

from app.services.partitioning import create_partition_sql, month_bounds, partition_name


def test_partition_name_pads_month():
    assert partition_name("interface_metrics", 2026, 7) == "interface_metrics_2026_07"
    assert partition_name("interface_metrics", 2026, 12) == "interface_metrics_2026_12"


def test_month_bounds_mid_year():
    assert month_bounds(2026, 7) == (date(2026, 7, 1), date(2026, 8, 1))


def test_month_bounds_december_rolls_into_next_year():
    assert month_bounds(2026, 12) == (date(2026, 12, 1), date(2027, 1, 1))


def test_create_partition_sql_contains_table_and_bounds():
    sql = create_partition_sql("interface_metrics", 2026, 7)

    assert '"interface_metrics_2026_07"' in sql
    assert '"interface_metrics"' in sql
    assert "'2026-07-01'" in sql
    assert "'2026-08-01'" in sql
