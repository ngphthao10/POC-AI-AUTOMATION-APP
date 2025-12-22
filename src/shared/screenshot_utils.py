"""
Screenshot utilities for debugging and documentation
"""
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from nova_act import NovaAct

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Manage screenshot capture for automation runs"""

    def __init__(
        self,
        base_dir: str = "screenshots",
        execution_id: Optional[str] = None,
        quality: int = 85
    ):
        """
        Initialize screenshot manager.

        Args:
            base_dir: Base directory for screenshots
            execution_id: Execution ID for organizing screenshots
            quality: JPEG quality (0-100)
        """
        if not execution_id:
            execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        self.execution_id = execution_id
        self.quality = quality
        self.screenshot_dir = Path(base_dir) / execution_id
        self.screenshot_count = 0

        # Create directory
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Screenshot directory: {self.screenshot_dir}")

    def capture(
        self,
        nova: NovaAct,
        name: str = None,
        step_name: str = None
    ) -> str:
        """
        Capture screenshot with automatic naming.

        Args:
            nova: NovaAct instance
            name: Optional custom name for screenshot
            step_name: Optional step name for context

        Returns:
            Path to saved screenshot

        Usage:
            manager = ScreenshotManager(execution_id='run_001')
            path = manager.capture(nova, step_name='login')
        """
        self.screenshot_count += 1

        # Generate filename
        timestamp = int(time.time())
        if name:
            filename = f"{timestamp}_{name}.jpg"
        elif step_name:
            filename = f"{timestamp}_{self.screenshot_count:03d}_{step_name}.jpg"
        else:
            filename = f"{timestamp}_{self.screenshot_count:03d}.jpg"

        filepath = self.screenshot_dir / filename

        try:
            # Capture screenshot
            nova.page.screenshot(
                path=str(filepath),
                type='jpeg',
                quality=self.quality
            )

            logger.info(f"Screenshot saved: {filepath}")
            print(f"📸 Screenshot: {filename}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            print(f"⚠️ Screenshot failed: {e}")
            return None

    def capture_with_timestamp(
        self,
        nova: NovaAct,
        prefix: str = "screenshot"
    ) -> str:
        """
        Capture screenshot with timestamp in filename.

        Args:
            nova: NovaAct instance
            prefix: Prefix for filename

        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        filename = f"{prefix}_{timestamp}.jpg"
        filepath = self.screenshot_dir / filename

        try:
            nova.page.screenshot(
                path=str(filepath),
                type='jpeg',
                quality=self.quality
            )
            logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None

    def capture_full_page(
        self,
        nova: NovaAct,
        name: str = "full_page"
    ) -> str:
        """
        Capture full page screenshot (scrolls to capture entire page).

        Args:
            nova: NovaAct instance
            name: Name for screenshot

        Returns:
            Path to saved screenshot
        """
        timestamp = int(time.time())
        filename = f"{timestamp}_{name}.jpg"
        filepath = self.screenshot_dir / filename

        try:
            nova.page.screenshot(
                path=str(filepath),
                type='jpeg',
                quality=self.quality,
                full_page=True
            )
            logger.info(f"Full page screenshot saved: {filepath}")
            print(f"📸 Full page screenshot: {filename}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to capture full page screenshot: {e}")
            return None

    def get_screenshot_dir(self) -> str:
        """Get the screenshot directory path."""
        return str(self.screenshot_dir)

    def get_screenshot_count(self) -> int:
        """Get number of screenshots captured."""
        return self.screenshot_count


def capture_screenshot(
    nova: NovaAct,
    filepath: str,
    quality: int = 85,
    full_page: bool = False
) -> bool:
    """
    Simple screenshot capture function.

    Args:
        nova: NovaAct instance
        filepath: Path where to save screenshot
        quality: JPEG quality (0-100)
        full_page: Capture full page or just viewport

    Returns:
        True if successful, False otherwise

    Usage:
        capture_screenshot(nova, 'screenshots/login.jpg')
    """
    try:
        # Create directory if needed
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Capture
        nova.page.screenshot(
            path=filepath,
            type='jpeg',
            quality=quality,
            full_page=full_page
        )

        logger.info(f"Screenshot saved: {filepath}")
        return True

    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        return False


def capture_screenshot_on_error(
    nova: NovaAct,
    error: Exception,
    base_dir: str = "screenshots/errors",
    execution_id: str = None
) -> str:
    """
    Capture screenshot when an error occurs for debugging.

    Args:
        nova: NovaAct instance
        error: Exception that occurred
        base_dir: Base directory for error screenshots
        execution_id: Execution ID

    Returns:
        Path to saved screenshot

    Usage:
        try:
            # automation code
        except Exception as e:
            capture_screenshot_on_error(nova, e, execution_id='run_001')
            raise
    """
    if not execution_id:
        execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    timestamp = int(time.time())
    error_name = type(error).__name__
    filename = f"{timestamp}_error_{error_name}.jpg"

    screenshot_dir = Path(base_dir) / execution_id
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    filepath = screenshot_dir / filename

    try:
        nova.page.screenshot(
            path=str(filepath),
            type='jpeg',
            quality=90
        )
        logger.error(f"Error screenshot saved: {filepath}")
        print(f"📸 Error screenshot: {filename}")
        return str(filepath)
    except Exception as screenshot_error:
        logger.error(f"Failed to capture error screenshot: {screenshot_error}")
        return None
