from datetime import datetime
from typing import List, Dict, Any

import structlog
from app.prometheus.client import PrometheusClient
from app.schemas.metrics import MetricData, MetricSeries, MetricPoint

logger = structlog.get_logger()

class PrometheusService:
    def __init__(self):
        self.client = PrometheusClient()

    async def get_metric_data(
        self, 
        query: str, 
        start: datetime, 
        end: datetime, 
        step: str = "5m", 
        metric_name: str = "Unknown Metric"
    ) -> MetricData:
        """
        Executes a range query and normalizes the result.
        """
        raw_data = await self.client.query_range(query, start, end, step)
        return self._normalize_response(raw_data, query, start, end, step, metric_name)

    def _normalize_response(
        self, 
        raw_data: Dict[str, Any], 
        query: str, 
        start: datetime, 
        end: datetime, 
        step: str,
        metric_name: str
    ) -> MetricData:
        """
        Converts Prometheus JSON format to MetricData.
        """
        status = raw_data.get("status")
        if status != "success":
            logger.error("prometheus_error", status=status, data=raw_data)
            raise ValueError(f"Prometheus query failed: {status}")

        result_type = raw_data.get("data", {}).get("resultType")
        results = raw_data.get("data", {}).get("result", [])

        series_list = []
        
        for res in results:
            labels = res.get("metric", {})
            values = res.get("values", []) # List of [timestamp, value]
            
            points = []
            vals = []
            for t, v in values:
                val_float = float(v)
                points.append(MetricPoint(timestamp=datetime.fromtimestamp(t), value=val_float))
                vals.append(val_float)
            
            # Simple aggregation
            min_val = min(vals) if vals else None
            max_val = max(vals) if vals else None
            avg_val = sum(vals) / len(vals) if vals else None

            series_list.append(MetricSeries(
                labels=labels,
                values=points,
                min_value=min_val,
                max_value=max_val,
                avg_value=avg_val
            ))

        return MetricData(
            metric_name=metric_name,
            query=query,
            start_time=start,
            end_time=end,
            step=step,
            series=series_list
        )
