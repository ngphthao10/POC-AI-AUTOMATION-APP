import time
import logging
from nova_act import NovaAct, BOOL_SCHEMA

logger = logging.getLogger(__name__)


def wait_for_loading_complete(
    nova: NovaAct,
    timeout_seconds: int = 60,
    action_description: str = "page to load",
    check_interval: int = 2
) -> bool:
    """
    Wait for loading indicators to disappear with timeout handling.
    This method only observes the page state and does NOT perform any clicks or actions.

    Args:
        nova: NovaAct instance
        timeout_seconds: Maximum time to wait for loading to complete (default 60 seconds)
        action_description: Description of what we're waiting for (for logging)
        check_interval: How often to check loading status in seconds (default 2)

    Returns:
        bool: True if loading completed within timeout, False if timeout occurred
    """
    start_time = time.time()
    logger.debug(f"Waiting for {action_description} (timeout: {timeout_seconds}s)")
    print(f"⏳ Waiting for {action_description}...")

    while time.time() - start_time < timeout_seconds:
        # Check for common loading indicators - OBSERVATION ONLY, NO ACTIONS
        is_loading = nova.act(
            "OBSERVE ONLY: Check if there are any loading indicators currently visible on the page: "
            "loading spinner, 'Loading...' text, progress bars, or modal dialogs with spinning wheels. "
            "Return True if any loading indicators are visible, False if page appears fully loaded. "
            "DO NOT click anything.",
            schema=BOOL_SCHEMA
        )

        if is_loading.matches_schema and not is_loading.parsed_response:
            # No loading indicators found - page is ready
            elapsed = time.time() - start_time
            logger.debug(f"Loading completed after {elapsed:.1f} seconds")
            print(f"✅ {action_description.title()} completed ({elapsed:.1f}s)")
            return True

        # Brief pause before checking again
        time.sleep(check_interval)
        elapsed = time.time() - start_time

        # Log progress every 10 seconds
        if int(elapsed) % 10 == 0 and int(elapsed) > 0:
            logger.debug(f"Still waiting for {action_description} ({elapsed:.0f}s elapsed)")
            print(f"⏳ Still waiting ({elapsed:.0f}s elapsed)...")

    # Timeout occurred
    elapsed = time.time() - start_time
    logger.error(f"Timeout waiting for {action_description} after {elapsed:.1f} seconds")
    print(f"❌ Timeout: {action_description} did not complete within {timeout_seconds} seconds")
    return False


def wait_for_element(
    nova: NovaAct,
    element_description: str,
    timeout_seconds: int = 30
) -> bool:
    """
    Wait for a specific element to appear on the page.

    Args:
        nova: NovaAct instance
        element_description: Description of element to wait for
        timeout_seconds: Maximum time to wait

    Returns:
        bool: True if element appeared, False if timeout
    """
    start_time = time.time()
    logger.debug(f"Waiting for element: {element_description}")
    print(f"⏳ Waiting for: {element_description}...")

    while time.time() - start_time < timeout_seconds:
        element_visible = nova.act(
            f"Check if the following element is visible on the page: {element_description}. "
            "Return True if visible, False if not.",
            schema=BOOL_SCHEMA
        )

        if element_visible.matches_schema and element_visible.parsed_response:
            elapsed = time.time() - start_time
            logger.debug(f"Element appeared after {elapsed:.1f} seconds")
            print(f"✅ Element found ({elapsed:.1f}s)")
            return True

        time.sleep(2)

    elapsed = time.time() - start_time
    logger.error(f"Timeout waiting for element: {element_description}")
    print(f"❌ Element not found within {timeout_seconds} seconds")
    return False


def wait_with_retry(
    nova: NovaAct,
    action_description: str,
    action_func,
    max_retries: int = 3,
    retry_delay: int = 2
) -> bool:
    """
    Execute an action with retry logic and wait for completion.

    Args:
        nova: NovaAct instance
        action_description: Description of the action
        action_func: Function to execute (should return bool)
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        bool: True if action succeeded, False otherwise
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.debug(f"Attempting {action_description} (attempt {attempt}/{max_retries})")
            print(f"🔄 {action_description} (attempt {attempt}/{max_retries})...")

            result = action_func()

            if result:
                logger.info(f"{action_description} succeeded on attempt {attempt}")
                print(f"✅ {action_description} succeeded")
                return True
            else:
                logger.warning(f"{action_description} returned False on attempt {attempt}")

        except Exception as e:
            logger.error(f"Error on attempt {attempt}: {str(e)}")
            print(f"⚠️ Attempt {attempt} failed: {str(e)}")

        if attempt < max_retries:
            logger.debug(f"Retrying in {retry_delay} seconds...")
            print(f"⏳ Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    logger.error(f"{action_description} failed after {max_retries} attempts")
    print(f"❌ {action_description} failed after {max_retries} attempts")
    return False
