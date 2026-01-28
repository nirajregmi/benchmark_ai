from dataclasses import dataclass

@dataclass
class RequestCompositionInfo:
    """Information about the composition of requests in a benchmark test."""
    history_count: int
    hit_data_percentage: float
    miss_data_percentage: float