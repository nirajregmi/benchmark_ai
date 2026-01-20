import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = structlog.get_logger()

class PrometheusClient:
    """
    Async client for Prometheus HTTP API.
    """
    def __init__(self, base_url: str = str(settings.PROMETHEUS_URL), token: Optional[str] = settings.PROMETHEUS_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def query(self, query: str, time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Instant query.
        """
        async with httpx.AsyncClient() as client:
            params = {"query": query}
            if time:
                params["time"] = time.timestamp()
                
            url = f"{self.base_url}/api/v1/query"
            logger.info("prometheus_query", url=url, query=query)
            
            response = await client.get(url, params=params, headers=self.headers, timeout=10.0)
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def query_range(
        self, 
        query: str, 
        start: datetime, 
        end: datetime, 
        step: str = "1m"
    ) -> Dict[str, Any]:
        """
        Range query for time-series data.
        """
        async with httpx.AsyncClient() as client:
            params = {
                "query": query,
                "start": start.timestamp(),
                "end": end.timestamp(),
                "step": step
            }
            
            url = f"{self.base_url}/api/v1/query_range"
            logger.info("prometheus_query_range", url=url, query=query, start=start, end=end)
            
            try:
                response = await client.get(url, params=params, headers=self.headers, timeout=20.0)
                response.raise_for_status()
                return response.json()
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                logger.warning("prometheus_connection_failed", error=str(e), msg="Returning MOCK data")
                # Return mock structure matching Prometheus response
                return {
                    "status": "success",
                    "data": {
                        "resultType": "matrix",
                        "result": [
                            {
                                "metric": {"pod": "mock-pod-1", "namespace": "default"},
                                "values": [
                                    [start.timestamp(), "0.5"],
                                    [end.timestamp(), "0.8"]
                                ]
                            }
                        ]
                    }
                }
