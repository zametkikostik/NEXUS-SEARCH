"""
Circuit Breaker Pattern Implementation
"""
import asyncio
import time
from typing import Dict, Optional, Callable, Any, TypeVar
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import httpx
from core.config import get_settings
from core.logging import get_logger
from core.exceptions import CircuitBreakerOpenException

settings = get_settings()
logger = get_logger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitStats:
    """Circuit breaker statistics"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: float = 0
    last_success_time: float = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class CircuitBreaker:
    """Circuit breaker for provider protection"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = None,
        recovery_timeout: int = None,
        timeout: int = None
    ):
        self.name = name
        self.failure_threshold = failure_threshold or settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self.recovery_timeout = recovery_timeout or settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT
        self.timeout = timeout or settings.CIRCUIT_BREAKER_TIMEOUT
        
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._lock = asyncio.Lock()
        self._half_open_successes = 0
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        async with self._lock:
            self.stats.total_calls += 1
            
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if time.time() - self.stats.last_failure_time > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self._half_open_successes = 0
                    logger.info(
                        "Circuit breaker half-open",
                        name=self.name,
                        consecutive_failures=self.stats.consecutive_failures
                    )
                else:
                    self.stats.rejected_calls += 1
                    raise CircuitBreakerOpenException(
                        provider=self.name,
                        retry_after=int(self.recovery_timeout - (time.time() - self.stats.last_failure_time))
                    )
        
        try:
            # Execute with timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.timeout
                )
            else:
                result = func(*args, **kwargs)
            
            await self._on_success()
            return result
            
        except asyncio.TimeoutError as e:
            await self._on_failure(e)
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                await self._on_failure(e)
            raise
        except Exception as e:
            await self._on_failure(e)
            raise
    
    async def _on_success(self) -> None:
        """Handle successful call"""
        async with self._lock:
            self.stats.successful_calls += 1
            self.stats.last_success_time = time.time()
            self.stats.consecutive_successes += 1
            self.stats.consecutive_failures = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= 2:
                    self.state = CircuitState.CLOSED
                    logger.info(
                        "Circuit breaker closed (recovered)",
                        name=self.name
                    )
    
    async def _on_failure(self, exception: Exception) -> None:
        """Handle failed call"""
        async with self._lock:
            self.stats.failed_calls += 1
            self.stats.last_failure_time = time.time()
            self.stats.consecutive_failures += 1
            self.stats.consecutive_successes = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning(
                    "Circuit breaker opened (half-open failed)",
                    name=self.name
                )
            elif self.stats.consecutive_failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(
                    "Circuit breaker opened",
                    name=self.name,
                    consecutive_failures=self.stats.consecutive_failures
                )
    
    def is_available(self) -> bool:
        """Check if circuit allows requests"""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.HALF_OPEN:
            return True
        # OPEN state - check recovery timeout
        return time.time() - self.stats.last_failure_time > self.recovery_timeout
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state"""
        return {
            "name": self.name,
            "state": self.state.value,
            "stats": {
                "total_calls": self.stats.total_calls,
                "successful_calls": self.stats.successful_calls,
                "failed_calls": self.stats.failed_calls,
                "rejected_calls": self.stats.rejected_calls,
                "consecutive_failures": self.stats.consecutive_failures,
                "consecutive_successes": self.stats.consecutive_successes,
            },
            "last_failure_time": self.stats.last_failure_time,
            "last_success_time": self.stats.last_success_time
        }
    
    def reset(self) -> None:
        """Reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._half_open_successes = 0


class CircuitBreakerRegistry:
    """Registry for circuit breakers"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, name: str) -> CircuitBreaker:
        """Get or create circuit breaker"""
        async with self._lock:
            if name not in self.breakers:
                self.breakers[name] = CircuitBreaker(name)
            return self.breakers[name]
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get all circuit breaker states"""
        return {name: cb.get_state() for name, cb in self.breakers.items()}
    
    async def reset(self, name: str) -> None:
        """Reset specific circuit breaker"""
        async with self._lock:
            if name in self.breakers:
                self.breakers[name].reset()
    
    async def reset_all(self) -> None:
        """Reset all circuit breakers"""
        async with self._lock:
            for cb in self.breakers.values():
                cb.reset()


# Global registry
circuit_breaker_registry = CircuitBreakerRegistry()


async def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Get circuit breaker for provider"""
    return await circuit_breaker_registry.get(name)


def with_circuit_breaker(name: str):
    """Decorator for circuit breaker"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cb = await get_circuit_breaker(name)
            return await cb.call(func, *args, **kwargs)
        return wrapper
    return decorator
