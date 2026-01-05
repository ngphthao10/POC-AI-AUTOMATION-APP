from nova_act import NovaAct, ActInvalidModelGenerationError, BOOL_SCHEMA
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.logger import setup_logger
from shared.retry_utils import format_error_for_display

logger = setup_logger(__name__)


class CSPRoleHandler:

    def __init__(self, nova: NovaAct):
        self.nova = nova
        self.page = nova.page

    def change_role(self, new_role: str) -> bool:
        try:
            logger.info(f"Changing role to: {new_role}")
            print(f"👤 Changing role to: {new_role}")

            # Step 0: Navigate to Roles tab
            logger.debug("Step 0: Navigating to Roles tab")
            print("  ➤ Navigating to Roles tab...")
            self.nova.act("Click the 'Roles' tab in the Edit user modal")
            time.sleep(2)

            # Check if role is already correct
            logger.debug(f"Checking if role is already set to: {new_role}")
            print(f"  ➤ Checking current role...")
            result = self.nova.act_get(
                f"Look at the FIRST Role field (top-most row). Does it already show '{new_role}'?",
                schema=BOOL_SCHEMA
            )
            if result.parsed_response:
                logger.info(f"Role already set to: {new_role}. Skipping update.")
                print(f"  ✓ Role already set to: {new_role}. No changes needed.")
                return True

            # Step 1: Open role dropdown
            logger.debug("Step 1: Opening role dropdown")
            print("  ➤ Opening role dropdown...")
            self.nova.act("In the FIRST Role row (top-most), click the dropdown arrow to open the role selector")
            time.sleep(1.5)

            # Step 2: Type role name to filter (Playwright - more reliable for typing)
            logger.debug(f"Step 2: Typing role name: {new_role}")
            print(f"  ➤ Searching for role: {new_role}...")

            self.nova.act("CLick the select search field in the open dropdown")
            time.sleep(1.5)

            # Clear search field first
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            time.sleep(0.3)

            # Type role name
            self.page.keyboard.type(new_role, delay=100)  # Type with delay for stability
            time.sleep(2)
            print(f"  ✓ Typed '{new_role}'")

            # Step 3: Click on the role (should be first/only result after filtering)
            logger.debug(f"Step 3: Selecting role from filtered list")
            print(f"  ➤ Clicking on role...")
            self.nova.act(f"In the dropdown list, click on the FIRST visible role option (should be '{new_role}' after filtering)")
            time.sleep(1.5)

            # Verify Step 3: Role is selected
            logger.debug("Verifying role is selected")
            try:
                result = self.nova.act_get(
                    f"Look at the FIRST Role field (top-most row). Does it now show '{new_role}' as the selected value?",
                    schema=BOOL_SCHEMA
                )
                if result.parsed_response:
                    logger.debug(f"✓ Verification PASSED - Role is selected")
                    print(f"  ✓ Role '{new_role}' selected successfully")
                else:
                    raise Exception(f"Role field should show '{new_role}'")
            except ActInvalidModelGenerationError as e:
                logger.error(f"Verification INVALID: {str(e)}")
                raise Exception(f"Failed to verify role selection: {str(e)}")

            logger.info(f"Role updated successfully to: {new_role}")
            print(f"✅ Role updated to: {new_role}")
            return True

        except Exception as e:
            logger.error(f"Role change failed: {str(e)}")
            error_msg = format_error_for_display(e, context="Role Change")
            print(error_msg)
            raise
