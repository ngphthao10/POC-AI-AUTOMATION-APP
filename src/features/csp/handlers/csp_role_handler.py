from nova_act import NovaAct
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.logger import setup_logger
from shared.retry_utils import with_retry
from shared.wait_utils import wait_for_loading_complete
from shared.error_utils import format_error_for_display
from shared.action_counter import ActionCounter

logger = setup_logger(__name__)


class CSPRoleHandler:

    def __init__(self, nova: NovaAct):
        self.nova = nova
        self.page = nova.page
        self.action_counter = ActionCounter(max_actions=30, step_name="RoleChange")

    @with_retry(max_retries=2, retry_delay=2)
    def change_role(self, new_role: str) -> bool:
        try:
            logger.info(f"Changing role to: {new_role}")
            print(f"👤 Changing role to: {new_role}")

            # Navigate to Roles tab first
            self.action_counter.safe_act(
                self.nova,
                "Click the 'Roles' tab in the Edit user modal"
            )
            time.sleep(1)

            # Wait for Roles tab to load
            if not wait_for_loading_complete(
                self.nova,
                timeout_seconds=20,
                action_description="Roles tab to load"
            ):
                raise Exception("Roles tab failed to load")

            # Step 1: Clear current role
            self.action_counter.safe_act(
                self.nova,
                "In the Role field, click the 'x' button to clear the current role value"
            )
            time.sleep(1)

            # Step 2: Open role dropdown
            self.action_counter.safe_act(
                self.nova,
                "Click the Role dropdown arrow to open the role selector"
            )
            time.sleep(1)

            # Step 3: Click search box in dropdown (Nova Act)
            self.action_counter.safe_act(
                self.nova,
                "Click the search input field inside the Role dropdown"
            )
            time.sleep(0.5)

            # Step 4: Type role name to filter (Playwright - reliable typing)
            logger.debug(f"Typing role name: {new_role}")
            self.page.keyboard.type(new_role)
            time.sleep(1.5)

            # Step 5: Select the role from filtered results
            self.action_counter.safe_act(
                self.nova,
                f"In the filtered role list, click on the role option that matches '{new_role}'"
            )
            time.sleep(1)

            logger.info(f"Role updated successfully to: {new_role}")
            print(f"✅ Role updated to: {new_role}")
            return True

        except Exception as e:
            logger.error(f"Role change failed: {str(e)}")
            error_msg = format_error_for_display(e, context="Role Change")
            print(error_msg)
            raise
