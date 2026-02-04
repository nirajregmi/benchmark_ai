import json
from typing import AsyncGenerator, Dict, Any, Optional

import httpx
import structlog
from app.core.config import settings
from app.llm.prompts import ANALYSIS_SYSTEM_PROMPT, INTENT_SYSTEM_PROMPT

logger = structlog.get_logger()

class LLMClient:

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = str(settings.LLM_API_URL).rstrip("/")
        self.model = settings.LLM_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_intent(self, user_query: str) -> Dict[str, Any]:

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0.1,  # Low temp for deterministic JSON
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions", 
                    json=payload, 
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
            except Exception as e:
                logger.error("llm_intent_error", error=str(e))
                return {"metric_type": "unknown", "time_range": "1h"}

    async def stream_analysis(self, user_query: str, metric_context: str) -> AsyncGenerator[str, None]:
        """
        Streams the analysis response from the LLM.
        """
        formatted_prompt = f"USER QUESTION:\n'{user_query}'\n\nCONTEXT:\n{metric_context}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": formatted_prompt}
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "stream": True
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", 
                f"{self.base_url}/chat/completions", 
                json=payload, 
                headers=self.headers,
                timeout=30.0
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        line = line[6:]  # Remove "data: " prefix
                        if line == "[DONE]":
                            break
                        try:
                            chunk = json.loads(line)
                            if chunk.get("choices") and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {}).get("content", "")
                                if delta:
                                    yield delta
                        except json.JSONDecodeError:
                            continue

    async def analyze_pod_comparison(self, pod1_name: str, pod2_name: str, pod1_metrics: Dict[str, Any], pod2_metrics: Dict[str, Any]) -> str:
        """
        Generate AI analysis comparing two pods' metrics.
        Returns the full analysis as a string.
        """
        from app.llm.prompts import POD_COMPARISON_PROMPT
        
        comparison_context = f"""
POD 1: {pod1_name}
CPU Usage: avg={pod1_metrics['cpu']['avg']:.4f}, max={pod1_metrics['cpu']['max']:.4f}, min={pod1_metrics['cpu']['min']:.4f}
Memory Usage: avg={pod1_metrics['memory']['avg']:.2f} bytes, max={pod1_metrics['memory']['max']:.2f}, min={pod1_metrics['memory']['min']:.2f}
CPU Throttling: avg={pod1_metrics['cpu_throttling']['avg']:.6f}, max={pod1_metrics['cpu_throttling']['max']:.6f}
Data Points: {pod1_metrics['cpu']['count']}

POD 2: {pod2_name}
CPU Usage: avg={pod2_metrics['cpu']['avg']:.4f}, max={pod2_metrics['cpu']['max']:.4f}, min={pod2_metrics['cpu']['min']:.4f}
Memory Usage: avg={pod2_metrics['memory']['avg']:.2f} bytes, max={pod2_metrics['memory']['max']:.2f}, min={pod2_metrics['memory']['min']:.2f}
CPU Throttling: avg={pod2_metrics['cpu_throttling']['avg']:.6f}, max={pod2_metrics['cpu_throttling']['max']:.6f}
Data Points: {pod2_metrics['cpu']['count']}

Time Period: 1 hour comparison
"""
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": POD_COMPARISON_PROMPT},
                {"role": "user", "content": f"Analyze and compare these two Kubernetes pods:\n\n{comparison_context}"}
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions", 
                    json=payload, 
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error("llm_comparison_error", error=str(e))
                return f"Error generating AI analysis: {str(e)}"
