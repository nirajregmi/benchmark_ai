from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class MetricPoint(BaseModel):
    """A single point in a time series."""
    timestamp: datetime
    value: float

class MetricSeries(BaseModel):
    """A series of metric points for a specific label set."""
    labels: Dict[str, str] = Field(default_factory=dict)
    values: List[MetricPoint] = Field(default_factory=list)
    
    # Aggregated stats for the LLM
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None

class MetricData(BaseModel):
    """
    Normalized metric data structure passed to the LLM.
    Abstracts away the raw Prometheus format.
    """
    metric_name: str
    query: str
    start_time: datetime
    end_time: datetime
    step: str
    series: List[MetricSeries] = Field(default_factory=list)

class PromQLResponse(BaseModel):
    """Raw response schema from Prometheus API (simplified)."""
    status: str
    data: Dict[str, Any]
