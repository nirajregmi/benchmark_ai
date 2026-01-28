from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class TimestampSeries:
    """One series with labels in 'metric' and datapoints in 'values'."""
    timestamps: List[datetime]
    values: List[float]
