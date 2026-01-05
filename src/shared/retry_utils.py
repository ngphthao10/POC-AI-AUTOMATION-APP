import time
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class RetryException(Exception):
    """Exception raised when all retry attempts are exhausted."""
    pass


# ============================================================================
# Error Classification & Formatting
# ============================================================================

def extract_error_message(error_str: str) -> str:
    """Extract clean error message from error string"""
    if not error_str:
        return "Unknown error"

    error_str = str(error_str).strip()

    # Check if it's an ActAgentError format
    if error_str.startswith("ActAgentError("):
        try:
            lines = error_str.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('message = '):
                    # Extract the message part after "message = "
                    message = line[10:].strip()
                    return message
        except Exception as e:
            logger.warning(f"Failed to parse ActAgentError format: {e}")

    # Check for other common error patterns
    if "message:" in error_str.lower():
        try:
            parts = error_str.split("message:", 1)
            if len(parts) > 1:
                message = parts[1].strip()
                # Remove any trailing metadata
                for delimiter in ['\n', 'metadata', 'session_id', 'act_id']:
                    if delimiter in message:
                        message = message.split(delimiter)[0].strip()
                return message
        except Exception as e:
            logger.warning(f"Failed to parse message: format: {e}")

    # Default: return first line
    first_line = error_str.split('\n')[0].strip()
    return first_line if first_line else error_str


def is_timeout_error(error: Exception) -> bool:
    """Check if error is timeout-related"""
    error_str = str(error).lower()
    return (
        'timeout' in error_str or
        'timeouterror' in error_str or
        'timed out' in error_str
    )


def is_network_error(error: Exception) -> bool:
    """Check if error is network-related"""
    error_str = str(error).lower()
    network_keywords = [
        'nameresolutionerror',
        'connection',
        'network',
        'dns',
        'unreachable',
        'max retries exceeded',
        'failed to resolve',
        'httpsconnectionpool',
        'connectionerror',
        'refused'
    ]
    return any(keyword in error_str for keyword in network_keywords)


def get_error_category(error: Exception) -> str:
    """Classify error into category"""
    error_str = str(error).lower()

    if 'nameresolutionerror' in error_str or 'dns' in error_str or 'failed to resolve' in error_str:
        return 'DNS_ERROR'
    elif 'connection' in error_str or 'refused' in error_str:
        return 'CONNECTION_ERROR'
    elif 'timeout' in error_str or 'timed out' in error_str:
        return 'TIMEOUT_ERROR'
    elif 'max retries exceeded' in error_str:
        return 'MAX_RETRIES_ERROR'
    else:
        return 'UNKNOWN_ERROR'


def format_error_for_display(error: Exception, context: str = "") -> str:
    """Format error for user-friendly display"""
    clean_msg = extract_error_message(str(error))

    if is_timeout_error(error):
        error_type = "⏱️ Timeout"
    elif is_network_error(error):
        error_type = "🌐 Network Error"
    else:
        error_type = "❌ Error"

    if context:
        return f"{error_type} ({context}): {clean_msg}"
    else:
        return f"{error_type}: {clean_msg}"


def get_retry_config_for_error(error: Exception) -> tuple:
    """
    Get recommended retry configuration for error type
    Returns: (should_retry, max_retries, initial_delay)
    """
    category = get_error_category(error)

    retry_configs = {
        'DNS_ERROR': (True, 5, 5),  # Retry 5 times, start with 5s delay
        'CONNECTION_ERROR': (True, 4, 3),  # Retry 4 times, 3s delay
        'TIMEOUT_ERROR': (True, 3, 2),  # Retry 3 times, 2s delay
        'MAX_RETRIES_ERROR': (False, 0, 0),  # Already retried
        'UNKNOWN_ERROR': (True, 2, 2)
    }

    return retry_configs.get(category, (True, 2, 2))


# ============================================================================
# Basic Retry Decorator (kept for backward compatibility in handlers)
# ============================================================================

def with_retry(
    func: Callable = None,
    max_retries: int = 3,
    retry_delay: int = 2,
    backoff_multiplier: float = 2.0,
    exceptions_to_retry: tuple = (Exception,),
    exceptions_to_skip: tuple = (),
    on_retry: Optional[Callable] = None
):
    """
    Decorator to retry a function on failure.

    Args:
        func: Function to wrap (provided automatically by decorator)
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff (e.g., 2.0 = double each time)
        exceptions_to_retry: Tuple of exceptions that should trigger a retry
        exceptions_to_skip: Tuple of exceptions that should NOT be retried
        on_retry: Optional callback function called on each retry (receives attempt number and exception)

    Usage:
        @with_retry(max_retries=3, retry_delay=2)
        def my_function():
            # code that might fail
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = retry_delay

            for attempt in range(1, max_retries + 1):
                try:
                    logger.debug(f"Executing {fn.__name__} (attempt {attempt}/{max_retries})")

                    if attempt > 1:
                        print(f"🔄 Retry attempt {attempt}/{max_retries} for {fn.__name__}")

                    result = fn(*args, **kwargs)

                    if attempt > 1:
                        logger.info(f"{fn.__name__} succeeded on retry attempt {attempt}")
                        print(f"✅ {fn.__name__} succeeded on attempt {attempt}")

                    return result

                except exceptions_to_skip as e:
                    # Don't retry these exceptions
                    logger.error(f"{fn.__name__} failed with non-retryable exception: {e}")
                    raise

                except exceptions_to_retry as e:
                    last_exception = e
                    logger.warning(f"{fn.__name__} attempt {attempt} failed: {str(e)}")
                    print(f"⚠️ Attempt {attempt} failed: {str(e)[:100]}")

                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt, e)
                        except Exception as callback_error:
                            logger.error(f"Retry callback error: {callback_error}")

                    # If not last attempt, wait before retrying
                    if attempt < max_retries:
                        logger.debug(f"Waiting {current_delay}s before retry...")
                        print(f"⏳ Waiting {current_delay}s before next attempt...")
                        time.sleep(current_delay)

                        # Exponential backoff
                        current_delay *= backoff_multiplier

            # All retries exhausted
            error_msg = f"{fn.__name__} failed after {max_retries} attempts. Last error: {last_exception}"
            logger.error(error_msg)
            print(f"❌ {fn.__name__} failed after {max_retries} attempts")
            raise RetryException(error_msg) from last_exception

        return wrapper

    # Support both @with_retry and @with_retry(max_retries=5)
    if func is None:
        return decorator
    else:
        return decorator(func)


# ============================================================================
# Network Circuit Breaker
# ============================================================================

class NetworkCircuitBreaker:
    """Circuit breaker for network operations"""

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.last_failure_time = None
        self.is_open = False

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        # If circuit is open, check if cooldown passed
        if self.is_open:
            if self.last_failure_time is None:
                elapsed = float('inf')
            else:
                elapsed = time.time() - self.last_failure_time

            if elapsed < self.cooldown_seconds:
                remaining = self.cooldown_seconds - int(elapsed)
                raise Exception(
                    f"⚡ Circuit breaker is OPEN. Network appears down. "
                    f"Wait {remaining}s before retry..."
                )
            else:
                # Try to close circuit (half-open state)
                self.is_open = False
                logger.info("Circuit breaker: Attempting recovery (half-open state)")
                print("🔄 Circuit breaker: Attempting recovery...")

        try:
            result = func(*args, **kwargs)
            # Success → reset counter
            if self.failure_count > 0:
                logger.info(f"Circuit breaker: Success after {self.failure_count} failures, resetting")
                print(f"✅ Circuit breaker: Recovered after {self.failure_count} failures")
            self.failure_count = 0
            return result

        except Exception as e:
            if is_network_error(e):
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.failure_threshold:
                    self.is_open = True
                    logger.error(
                        f"Circuit breaker OPENED after {self.failure_count} consecutive network failures"
                    )
                    print(f"⚡ Circuit breaker OPEN after {self.failure_count} network failures")
                    print(f"   Will wait {self.cooldown_seconds}s before retry...")

            raise
