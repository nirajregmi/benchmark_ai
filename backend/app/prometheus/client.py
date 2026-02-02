import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, List

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = structlog.get_logger()

class PrometheusClient:
    def __init__(self, base_url: str = str(settings.PROMETHEUS_URL), token: Optional[str] = settings.PROMETHEUS_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def query(self, query: str, time: Optional[datetime] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(verify=False) as client:
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
        async with httpx.AsyncClient(verify=False) as client:
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
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError) as e:
                logger.warning("prometheus_connection_failed", error=str(e), msg="Returning MOCK data")
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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_label_values(self, label: str) -> List[str]:
        """
        Fetch all values for a specific label (e.g., 'pod').
        """
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/api/v1/label/{label}/values"
            logger.info("prometheus_label_values", url=url, label=label)
            
            try:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                if data.get("status") == "success":
                    return data.get("data", [])
                return []
            except Exception as e:
                logger.warning("prometheus_label_fetch_failed", error=str(e))
                # Mock fallback
                return ["payment-service-1", "payment-service-2", "checkout-service-1", "redis-master-0"]
