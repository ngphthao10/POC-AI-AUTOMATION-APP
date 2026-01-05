"""
Handler Wrapper - Wrap handler calls với retry logic
"""

import logging
import time
from typing import Callable

from src.shared.retry_utils import (
    NetworkCircuitBreaker,
    is_network_error,
    get_error_category
)

logger = logging.getLogger(__name__)

# Global circuit breaker
circuit_breaker = NetworkCircuitBreaker(failure_threshold=3, cooldown_seconds=60)


class HandlerWrapper:
    """
    Wrapper cho handler calls - thêm retry logic
    Handlers gốc GIỮ NGUYÊN 100%
    """

    def execute_with_retry(
        self,
        step_name: str,
        handler_func: Callable,
        max_retries: int = 5,
        *args,
        **kwargs
    ) -> bool:
        """
        Execute handler với retry logic

        Args:
            step_name: Tên bước (để log)
            handler_func: Handler function GỐC (không sửa)
            max_retries: Max retry attempts
            *args, **kwargs: Arguments cho handler

        Returns:
            True if success, False if failed
        """

        # Execute with smart retry
        for attempt in range(max_retries):
            try:
                logger.info(f"Executing {step_name} (attempt {attempt + 1}/{max_retries})")
                print(f"  ▶️  {step_name} (attempt {attempt + 1}/{max_retries})")

                # Execute handler với circuit breaker
                result = circuit_breaker.call(handler_func, *args, **kwargs)

                # Success
                print(f"  ✅ {step_name} completed")
                return True

            except Exception as e:
                error_category = get_error_category(e)
                logger.error(f"Step {step_name} failed: {error_category} - {str(e)[:100]}")
                print(f"  ❌ {step_name} failed: {error_category}")

                # Check if can retry
                if attempt < max_retries - 1:
                    # Calculate delay based on error type
                    if is_network_error(e):
                        delay = 5 * (2 ** attempt)  # Exponential: 5s, 10s, 20s, 40s, 80s
                    else:
                        delay = 2 * (attempt + 1)   # Linear: 2s, 4s, 6s

                    delay = min(delay, 120)  # Cap at 120s

                    print(f"  ⏳ Waiting {delay}s before retry...")
                    logger.info(f"Retrying {step_name} after {delay}s")
                    time.sleep(delay)
                else:
                    # Max retries reached
                    logger.error(f"Step {step_name} failed after {max_retries} attempts")
                    print(f"  ❌ {step_name} failed after {max_retries} attempts")
                    return False

        return False
