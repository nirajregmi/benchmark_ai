
from datetime import datetime, timedelta
import io
from typing import List, Dict

import structlog

from app.llm.client import LLMClient
from app.prometheus.service import PrometheusService
from app.services.promql_builder import build_promql_query
from app.report_gen.report_service import ReportService
from app.report_gen.models.benchmark_data import BenchmarkData
from app.report_gen.models.benchmarking_info import BenchmarkingInfo
from app.report_gen.models.timestamp_series import TimestampSeries
from app.report_gen.models.deployment_info import DeploymentInfo
from app.report_gen.models.request_composition_info import RequestCompositionInfo

logger = structlog.get_logger()

class ReportBridge:
    def __init__(self):
        self.prom_service = PrometheusService()
        self.report_service = ReportService()
        self.llm_client = LLMClient()

    async def generate_comparison_report(self, selected_pods: List[str]) -> io.BytesIO:
        """
        Generates a DOCX report comparing the first two pods in the list.
        """
        if len(selected_pods) < 2:
            raise ValueError("At least two pods are required for a comparison report.")

        pod1 = selected_pods[0]
        pod2 = selected_pods[1]
        
        # 1. Fetch Data
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1) # Default 1h report

        data_pod1 = await self._fetch_pod_data(pod1, start_time, end_time)
        data_pod2 = await self._fetch_pod_data(pod2, start_time, end_time)

        # Generate AI comparison analysis
        logger.info("generating_ai_analysis", pod1=pod1, pod2=pod2)
        pod1_stats = self._calculate_metrics_stats(data_pod1)
        pod2_stats = self._calculate_metrics_stats(data_pod2)
        ai_analysis = await self.llm_client.analyze_pod_comparison(pod1, pod2, pod1_stats, pod2_stats)
        logger.info("ai_analysis_complete")

        # 2. Benchmark Data Construction
        release1 = BenchmarkData(
            pod_name=pod1,
            cpu_usage=data_pod1['cpu'],
            memory_usage=data_pod1['memory'],
            cpu_throttling=data_pod1['cpu_throttling'],
            waah_version="1.0.0", # Placeholder/Mock
            waah_taxonomy_version="1.0.0",
            waah_kernel_version="5.15"
        )

        release2 = BenchmarkData(
            pod_name=pod2,
            cpu_usage=data_pod2['cpu'],
            memory_usage=data_pod2['memory'],
            cpu_throttling=data_pod2['cpu_throttling'],
            waah_version="1.0.1", # Placeholder/Mock
            waah_taxonomy_version="1.0.0",
            waah_kernel_version="5.15"
        )

        # 3. Benchmark Info Construction (Mock/Defaults)
        info = BenchmarkingInfo(
            story_name="AI-Powered Pod Comparison Report",
            edit_name=f"Comparison: {pod1} vs {pod2}",
            branch_name="main",
            tba_claims=["AI-generated performance analysis"],
            request_composition=[
                RequestCompositionInfo(history_count=100, hit_data_percentage=20.0, miss_data_percentage=80.0)
            ],
            deployment_info=DeploymentInfo(
                cpu_limits="1000m",
                memory_limits="1Gi",
                heap_size="512Mi",
                cpu_requests="500m",
                memory_requests="512Mi"
            )
        )

        # 4. Generate Report with AI Analysis
        try:
            doc = self.report_service.generate_report(release1, release2, info, ai_analysis=ai_analysis)
        except Exception as e:
            logger.error("report_generation_error", error=str(e), pod1=pod1, pod2=pod2)
            raise
        
        # 5. Return Bytes
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.flush()  # Ensure all data is written
        buffer.seek(0)  # Reset to beginning for reading
        return buffer

    async def _fetch_pod_data(self, pod_name: str, start: datetime, end: datetime) -> Dict[str, TimestampSeries]:
        metrics = {}
        for metric_type in ['cpu', 'memory', 'cpu_throttling']:
            # We explicitly filter by just ONE pod here to get its specific series
            query = build_promql_query(metric_type, selected_pods=[pod_name]) 
            
            # PrometheusService returns Pydantic models (MetricData -> MetricSeries)
            result = await self.prom_service.get_metric_data(query, start, end, step="1m", metric_name=metric_type)
            
            timestamps = []
            values = []
            
            # Extract data from the first series found (should be only one due to pod filter)
            if result.series:
                s = result.series[0]
                if s.values:
                     for point in s.values:
                         timestamps.append(point.timestamp)
                         values.append(point.value)
            
            metrics[metric_type] = TimestampSeries(timestamps=timestamps, values=values)
            
        return metrics

    def _calculate_metrics_stats(self, metrics_data: Dict[str, TimestampSeries]) -> Dict[str, Dict[str, float]]:
        """Calculate statistics (avg, max, min) for each metric type."""
        stats = {}
        for metric_type, series in metrics_data.items():
            if series.values:
                stats[metric_type] = {
                    'avg': sum(series.values) / len(series.values),
                    'max': max(series.values),
                    'min': min(series.values),
                    'count': len(series.values)
                }
            else:
                stats[metric_type] = {
                    'avg': 0.0,
                    'max': 0.0,
                    'min': 0.0,
                    'count': 0
                }
        return stats
