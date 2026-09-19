import httpx
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential


class HttpClient:
    """HTTP client with retry logic and connection pooling"""
    
    def __init__(self, timeout: int = 15, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get(self, url: str, **kwargs) -> Optional[httpx.Response]:
        """GET request with retry logic"""
        try:
            response = await self.client.get(url, **kwargs)
            return response
        except httpx.TimeoutException:
            return None
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
