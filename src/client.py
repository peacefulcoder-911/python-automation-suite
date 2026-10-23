import asyncio
import logging
from typing import Any, Dict, Optional
import httpx
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class APIClient:
    """Production-grade async HTTP client with retry logic and telemetry."""

    def __init__(self, base_url: str = "", timeout: float = 10.0, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"User-Agent": "PythonAutomationSuite/1.0"},
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        client = await self.get_client()
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                return {
                    "status_code": response.status_code,
                    "data": response.json() if "application/json" in response.headers.get("content-type", "") else response.text,
                    "latency_ms": round(response.elapsed.total_seconds() * 1000, 2),
                    "success": True,
                }
            except (httpx.HTTPError, httpx.RequestError) as err:
                last_exception = err
                wait_time = 2 ** attempt
                if attempt < self.max_retries:
                    await asyncio.sleep(wait_time)

        return {
            "status_code": None,
            "error": str(last_exception),
            "latency_ms": None,
            "success": False,
        }

    async def check_endpoint(self, name: str, url: str) -> Dict[str, Any]:
        """Performs a health and latency check on an endpoint."""
        client = await self.get_client()
        try:
            resp = await client.get(url)
            latency = round(resp.elapsed.total_seconds() * 1000, 2)
            return {
                "name": name,
                "url": url,
                "status_code": resp.status_code,
                "latency_ms": latency,
                "healthy": resp.status_code < 400,
            }
        except Exception as e:
            return {
                "name": name,
                "url": url,
                "status_code": None,
                "latency_ms": None,
                "healthy": False,
                "error": str(e),
            }