from dataclasses import dataclass

from app.report_gen.models.timestamp_series import TimestampSeries


@dataclass
class BenchmarkData:

    """Benchmark data containing multiple timestamp series."""
    pod_name: str
    cpu_usage: TimestampSeries
    memory_usage: TimestampSeries
    cpu_throttling: TimestampSeries
    waah_version: str
    waah_taxonomy_version: str
    waah_kernel_version: str