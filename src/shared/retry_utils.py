import time
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class RetryException(Exception):
    """Exception raised when all retry attempts are exhausted."""
    pass


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

        # Or with custom config
        @with_retry(max_retries=5, backoff_multiplier=1.5, exceptions_to_retry=(TimeoutError,))
        def another_function():
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


def retry_on_failure(
    action_func: Callable,
    max_retries: int = 3,
    retry_delay: int = 2,
    action_name: str = "Action"
) -> Any:
    """
    Execute a function with retry logic (non-decorator version).

    Args:
        action_func: Function to execute
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        action_name: Name of the action for logging

    Returns:
        Result from action_func

    Raises:
        RetryException: If all retries fail

    Usage:
        result = retry_on_failure(
            lambda: my_risky_operation(),
            max_retries=3,
            action_name="Database query"
        )
    """
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.debug(f"Executing {action_name} (attempt {attempt}/{max_retries})")

            if attempt > 1:
                print(f"🔄 {action_name} - retry attempt {attempt}/{max_retries}")

            result = action_func()

            if attempt > 1:
                logger.info(f"{action_name} succeeded on attempt {attempt}")
                print(f"✅ {action_name} succeeded on attempt {attempt}")

            return result

        except Exception as e:
            last_exception = e
            logger.warning(f"{action_name} attempt {attempt} failed: {str(e)}")
            print(f"⚠️ Attempt {attempt} failed: {str(e)[:100]}")

            if attempt < max_retries:
                logger.debug(f"Waiting {retry_delay}s before retry...")
                print(f"⏳ Waiting {retry_delay}s before retry...")
                time.sleep(retry_delay * attempt)  # Linear backoff

    # All retries exhausted
    error_msg = f"{action_name} failed after {max_retries} attempts. Last error: {last_exception}"
    logger.error(error_msg)
    print(f"❌ {action_name} failed after all attempts")
    raise RetryException(error_msg) from last_exception


class RetryStrategy:
    """
    Configurable retry strategy with multiple backoff options.

    Usage:
        strategy = RetryStrategy(max_retries=5, strategy='exponential')
        result = strategy.execute(my_function, arg1, arg2)
    """

    STRATEGIES = ['linear', 'exponential', 'fixed']

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: int = 2,
        strategy: str = 'exponential',
        max_delay: int = 60
    ):
        """
        Initialize retry strategy.

        Args:
            max_retries: Maximum retry attempts
            base_delay: Base delay in seconds
            strategy: 'linear', 'exponential', or 'fixed'
            max_delay: Maximum delay cap in seconds
        """
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Strategy must be one of {self.STRATEGIES}")

        self.max_retries = max_retries
        self.base_delay = base_delay
        self.strategy = strategy
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        if self.strategy == 'fixed':
            delay = self.base_delay
        elif self.strategy == 'linear':
            delay = self.base_delay * attempt
        else:  # exponential
            delay = self.base_delay * (2 ** (attempt - 1))

        # Cap at max_delay
        return min(delay, self.max_delay)

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with configured retry strategy."""
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    delay = self.get_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt} failed, retrying in {delay}s (strategy: {self.strategy})"
                    )
                    time.sleep(delay)

        raise RetryException(
            f"All {self.max_retries} attempts failed"
        ) from last_exception
