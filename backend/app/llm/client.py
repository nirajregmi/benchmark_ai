import json
from typing import AsyncGenerator, Dict, Any, Optional

import httpx
import structlog
from app.core.config import settings
from app.llm.prompts import ANALYSIS_SYSTEM_PROMPT, INTENT_SYSTEM_PROMPT

logger = structlog.get_logger()

class LLMClient:
    """
    Client for interacting with LLaMA-3.3-70B via compatible API.
    """
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = str(settings.LLM_API_URL).rstrip("/")
        self.model = settings.LLM_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Extracts intent from user query as JSON.
        """
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
                # Fallback to defaults
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
            "stream": True # Enable streaming
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
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            continue
