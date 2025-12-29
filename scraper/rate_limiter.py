"""
Rate limiting and retry utilities for polite scraping.
"""
import asyncio
import aiohttp
import logging
from typing import Optional
from functools import wraps
import random

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Token bucket rate limiter for async operations.
    """
    
    def __init__(self, rate: float = 2.0, burst: int = 5):
        """
        Args:
            rate: Requests per second
            burst: Maximum burst size (token bucket capacity)
        """
        self.rate = rate
        self.burst = burst
        self._tokens = burst
        self._last_update = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Wait until a request can be made within rate limits.
        """
        async with self._lock:
            now = asyncio.get_event_loop().time()
            
            # Replenish tokens based on time elapsed
            elapsed = now - self._last_update
            self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
            self._last_update = now
            
            if self._tokens < 1:
                # Need to wait
                wait_time = (1 - self._tokens) / self.rate
                logger.debug(f"Rate limited, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self._tokens = 0
            else:
                self._tokens -= 1


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt (0-indexed)."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay


async def fetch_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    method: str = "GET",
    retry_config: Optional[RetryConfig] = None,
    rate_limiter: Optional[RateLimiter] = None,
    **kwargs
) -> Optional[aiohttp.ClientResponse]:
    """
    Fetch a URL with retry logic and optional rate limiting.
    
    Returns the response object or None if all retries failed.
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(retry_config.max_retries + 1):
        try:
            # Apply rate limiting
            if rate_limiter:
                await rate_limiter.acquire()
            
            # Make request
            if method.upper() == "GET":
                response = await session.get(url, **kwargs)
            elif method.upper() == "POST":
                response = await session.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check for success
            if response.status == 200:
                return response
            elif response.status == 429:  # Too Many Requests
                logger.warning(f"Rate limited by server (429) on attempt {attempt + 1}")
                await response.release()
            elif response.status >= 500:  # Server errors
                logger.warning(f"Server error {response.status} on attempt {attempt + 1}")
                await response.release()
            else:
                # Client error (4xx) - don't retry
                logger.warning(f"Client error {response.status} for {url}")
                return response
                
        except aiohttp.ClientError as e:
            last_exception = e
            logger.warning(f"Request error on attempt {attempt + 1}: {e}")
        except asyncio.TimeoutError:
            last_exception = asyncio.TimeoutError()
            logger.warning(f"Timeout on attempt {attempt + 1}")
        
        # Wait before retry
        if attempt < retry_config.max_retries:
            delay = retry_config.get_delay(attempt)
            logger.debug(f"Retrying in {delay:.2f}s...")
            await asyncio.sleep(delay)
    
    if last_exception:
        logger.error(f"All retries failed for {url}: {last_exception}")
    
    return None


class Semaphore:
    """
    Wrapper around asyncio.Semaphore for limiting concurrent requests.
    """
    
    def __init__(self, max_concurrent: int = 5):
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def __aenter__(self):
        await self._semaphore.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._semaphore.release()
