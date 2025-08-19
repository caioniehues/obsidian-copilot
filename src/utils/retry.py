"""
Retry mechanism utilities with exponential backoff and circuit breaker patterns.
Provides robust error recovery for external service calls.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Any, Optional, Type, Union, Tuple
from enum import Enum

from src.exceptions import ServiceUnavailableError, TimeoutError

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, not allowing calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker implementation for service resilience."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise ServiceUnavailableError(
                        f"Circuit breaker is OPEN. Service unavailable.",
                        error_code="CIRCUIT_BREAKER_OPEN"
                    )
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
        
        logger.warning(
            f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}. "
            f"State: {self.state.value}"
        )


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to prevent thundering herd
        exceptions: Exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                        raise
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    if jitter:
                        import random
                        delay *= (0.5 + random.random() / 2)  # Add 25-75% jitter
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    
                    await asyncio.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception or Exception("Unknown error in retry mechanism")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                        raise
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    if jitter:
                        import random
                        delay *= (0.5 + random.random() / 2)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    
                    time.sleep(delay)
            
            raise last_exception or Exception("Unknown error in retry mechanism")
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


async def timeout_wrapper(
    coro: Callable,
    timeout_seconds: float,
    timeout_message: Optional[str] = None
) -> Any:
    """
    Wrapper for adding timeout to async operations.
    
    Args:
        coro: Coroutine to execute
        timeout_seconds: Timeout in seconds
        timeout_message: Custom timeout message
    
    Raises:
        TimeoutError: If operation times out
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        message = timeout_message or f"Operation timed out after {timeout_seconds}s"
        raise TimeoutError(message, error_code="OPERATION_TIMEOUT")


class HealthChecker:
    """Health checker for external services with circuit breaker integration."""
    
    def __init__(self, circuit_breaker: Optional[CircuitBreaker] = None):
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.last_health_check: Optional[float] = None
        self.health_check_interval = 30.0  # seconds
        self._is_healthy = False
    
    @property
    def is_healthy(self) -> bool:
        """Check if service is currently healthy."""
        return self._is_healthy and self.circuit_breaker.state != CircuitState.OPEN
    
    async def check_health(self, health_check_func: Callable) -> bool:
        """
        Perform health check using provided function.
        
        Args:
            health_check_func: Async function that returns True if healthy
        
        Returns:
            True if service is healthy
        """
        current_time = time.time()
        
        # Skip if recently checked
        if (self.last_health_check and 
            current_time - self.last_health_check < self.health_check_interval):
            return self._is_healthy
        
        try:
            self._is_healthy = await health_check_func()
            self.last_health_check = current_time
            return self._is_healthy
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            self._is_healthy = False
            return False


# Pre-configured retry decorators for common scenarios
opensearch_retry = retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    exceptions=(ConnectionError, TimeoutError, ServiceUnavailableError)
)

redis_retry = retry_with_backoff(
    max_retries=2,
    base_delay=0.5,
    max_delay=5.0,
    exceptions=(ConnectionError, TimeoutError)
)

api_retry = retry_with_backoff(
    max_retries=3,
    base_delay=2.0,
    max_delay=30.0,
    exceptions=(ServiceUnavailableError, TimeoutError)
)