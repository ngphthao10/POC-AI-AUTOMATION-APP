from nova_act import NovaAct
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.logger import setup_logger
from shared.retry_utils import with_retry
from shared.error_utils import format_error_for_display
from shared.screenshot_utils import capture_screenshot_on_error

logger = setup_logger(__name__)


class CSPLoginHandler:

    def __init__(self, nova: NovaAct, screenshot_manager=None):
        self.nova = nova
        self.page = nova.page
        self.screenshot_manager = screenshot_manager

    @with_retry(max_retries=3, retry_delay=2)
    def login(self, username: str, password: str) -> bool:
        try:
            logger.info(f"Starting login for user: {username}")
            print(f"🔐 Logging in as: {username}")

            # Wait for page load
            time.sleep(2)

            # Fill username
            if not self._fill_username(username):
                raise Exception("Failed to fill username")

            time.sleep(0.5)

            # Fill password
            if not self._fill_password(password):
                raise Exception("Failed to fill password")

            time.sleep(0.5)

            # Submit
            if not self._submit_login():
                raise Exception("Failed to submit login")

            print("✓ Login submitted")
            time.sleep(3)

            # Verify success
            if not self._verify_login():
                raise Exception("Login verification failed - Administration menu not found")

            # Screenshot on success if manager available
            if self.screenshot_manager:
                self.screenshot_manager.capture(self.nova, step_name="login_success")

            logger.info("Login successful")
            print("✅ Login successful")
            return True

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")

            # Screenshot on error
            if self.screenshot_manager:
                capture_screenshot_on_error(
                    self.nova, e,
                    base_dir=self.screenshot_manager.get_screenshot_dir()
                )

            # Display formatted error
            error_msg = format_error_for_display(e, context="Login")
            print(error_msg)
            raise

    def _fill_username(self, username: str) -> bool:
        username_selectors = ["input[name='username']", "input[type='text']", "input:first-of-type"]

        for selector in username_selectors:
            try:
                locator = self.page.locator(selector).first
                if locator.count() > 0:
                    locator.fill(username)
                    logger.debug(f"Username filled using selector: {selector}")
                    print("✓ Username filled")
                    return True
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue

        logger.error("All username selectors failed")
        return False

    def _fill_password(self, password: str) -> bool:
        password_selectors = ["input[name='password']", "input[type='password']"]

        for selector in password_selectors:
            try:
                locator = self.page.locator(selector).first
                if locator.count() > 0:
                    locator.fill(password)
                    logger.debug(f"Password filled using selector: {selector}")
                    print("✓ Password filled")
                    return True
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue

        logger.error("All password selectors failed")
        return False

    def _submit_login(self) -> bool:
        try:
            button = self.page.locator("button[type='submit']").first
            if button.count() > 0:
                button.click()
                logger.debug("Login submitted via button")
            else:
                self.page.keyboard.press("Enter")
                logger.debug("Login submitted via Enter key")
            return True
        except Exception as e:
            logger.error(f"Submit failed: {e}")
            return False

    def _verify_login(self) -> bool:
        try:
            self.page.wait_for_selector("text='Administration'", timeout=5000)
            logger.debug("Login verified - Administration menu found")
            return True
        except Exception as e:
            logger.error(f"Login verification failed: {e}")
            return False
