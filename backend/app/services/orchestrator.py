import json
from datetime import datetime, timedelta
from typing import AsyncGenerator, List

import structlog
from app.llm.client import LLMClient
from app.prometheus.service import PrometheusService
from app.services.promql_builder import build_promql_query

logger = structlog.get_logger()

class IntelligenceOrchestrator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.prom_service = PrometheusService()

    async def process_user_query(self, user_query: str, selected_pods: List[str] = []) -> AsyncGenerator[str, None]:
        """
        Main pipeline:
        1. Detect Intent
        2. Build PromQL
        3. Fetch Metrics
        4. Stream LLM Analysis
        """
        logger.info("processing_query", query=user_query)

        # Step 1: Detect Intent
        intent = await self.llm_client.generate_intent(user_query)
        logger.info("intent_detected", intent=intent)

        metric_type = intent.get("metric_type", "unknown")
        resource_name = intent.get("resource_name")
        time_range = intent.get("time_range", "1h")

        # Step 2: Time Range Calculation
        end_time = datetime.now()
        start_time = self._calculate_start_time(end_time, time_range)

        # Step 3: Build Query & Fetch Data
        try:
            if metric_type != "unknown":
                query = build_promql_query(metric_type, resource_name, selected_pods)
                metric_data = await self.prom_service.get_metric_data(
                    query=query,
                    start=start_time,
                    end=end_time,
                    metric_name=f"{metric_type} usage"
                )
                # Convert to simple JSON/Success string for LLM Context
                context_str = metric_data.model_dump_json(exclude={'series': {'__all__': {'values'}}}) 
                # Note: We exclude raw values to save tokens, focusing on aggs if possible, 
                # but currently our schema has aggs in the series. 
                # Let's just dump a simplified version.
                context_str = self._simplify_context(metric_data)
            else:
                context_str = "No specific metric identified. Answer based on general knowledge or ask for clarification."
        except Exception as e:
            logger.error("metric_fetch_failed", error=str(e))
            context_str = f"Error fetching metrics: {str(e)}"

        # Step 4: Stream LLM Response
        async for chunk in self.llm_client.stream_analysis(user_query, context_str):
            yield chunk

    def _calculate_start_time(self, end_time: datetime, range_str: str) -> datetime:
        if range_str == "24h":
            return end_time - timedelta(hours=24)
        elif range_str == "7d":
            return end_time - timedelta(days=7)
        else: # Default 1h
            return end_time - timedelta(hours=1)

    def _simplify_context(self, metric_data) -> str:
        """
        Create a token-efficient summary of the data.
        """
        summary = {
            "metric": metric_data.metric_name,
            "period": f"{metric_data.start_time} to {metric_data.end_time}",
            "series_highlights": []
        }
        for s in metric_data.series:
            summary["series_highlights"].append({
                "labels": s.labels,
                "avg": f"{s.avg_value:.2f}" if s.avg_value is not None else "N/A",
                "peak": f"{s.max_value:.2f}" if s.max_value is not None else "N/A",
                "min": f"{s.min_value:.2f}" if s.min_value is not None else "N/A",
            })
        return json.dumps(summary, indent=2)
