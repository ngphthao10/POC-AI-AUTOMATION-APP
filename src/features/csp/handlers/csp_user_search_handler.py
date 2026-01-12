from nova_act import NovaAct
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.logger import setup_logger
from shared.retry_utils import format_error_for_display

logger = setup_logger(__name__)


class CSPUserSearchHandler:

    def __init__(self, nova: NovaAct):
        self.nova = nova
        self.page = nova.page

    def search_and_open_edit(self, target_user: str) -> bool:
        """
        Search for user and open edit form with retry logic

        Args:
            target_user: Username to search

        Returns:
            True if edit form opened
        """
        try:
            logger.info(f"Searching for user: {target_user}")
            print(f"🔍 Searching for user: {target_user}")

            # Expand filters (Nova Act)
            self.nova.act("Click 'More filters' if visible")
            time.sleep(0.5)

            # Click Login field (Nova Act)
            self.nova.act("Click the Login field")
            time.sleep(0.3)

            # Clear and type username (Playwright - secure, no username in AI logs)
            self.page.keyboard.press("Control+A")  # Select all
            self.page.keyboard.press("Backspace")  # Select all
            self.page.keyboard.type(target_user)
            time.sleep(0.3)
            logger.debug(f"Username typed: {target_user}")

            # Search (Nova Act)
            self.nova.act("Click the Search button")
            time.sleep(2)  # Quick wait for search results

            # Open edit form (Nova Act)
            # self.nova.act("In the results table, click the first row's Actions dropdown and select Edit")
            self.nova.act("In the results table, click the first row's Actions dropdown")
            time.sleep(1)
            self.nova.act("In the dropdown menu, click Edit")
            time.sleep(2)  # Wait for edit form to load

            logger.info(f"Edit form opened successfully for {target_user}")
            print(f"✅ Edit form opened for {target_user}")
            return True

        except Exception as e:
            logger.error(f"Search and open edit failed: {str(e)}")
            error_msg = format_error_for_display(e, context="User Search")
            print(error_msg)
            raise
