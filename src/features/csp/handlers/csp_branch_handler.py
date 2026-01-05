from nova_act import NovaAct, ActInvalidModelGenerationError, BOOL_SCHEMA
from typing import List
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.logger import setup_logger
from shared.retry_utils import format_error_for_display

logger = setup_logger(__name__)


class CSPBranchHandler:

    def __init__(self, nova: NovaAct):
        self.nova = nova
        self.page = nova.page

    def change_branch_hierarchical(self, branch_hierarchy: List[str]) -> bool:
        try:
            if not branch_hierarchy or len(branch_hierarchy) < 3:
                error_msg = "Invalid branch hierarchy (need at least 3 levels)"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                return False

            bank, region, branch = branch_hierarchy[0], branch_hierarchy[1], branch_hierarchy[2]
            logger.info(f"Changing branch to: {bank} -> {region} -> {branch}")

            # Ensure on Roles tab
            self.nova.act("Click the 'Roles' tab in the Edit user modal")
            time.sleep(1)

            # Step 1: Change Bank User
            self._change_bank_user(bank, region, branch)

            # Step 2: Change Scope
            self._change_scope(bank, region, branch)

            logger.info(f"Branch changed successfully to: {branch}")
            print(f"✅ Branch changed successfully to: {branch}")
            return True

        except Exception as e:
            logger.error(f"Branch change failed: {str(e)}")
            error_msg = format_error_for_display(e, context="Branch Change")
            print(error_msg)
            raise

    def _change_bank_user(self, bank: str, region: str, branch: str):
        logger.debug("Changing Bank User...")
        print("🏦 Step 1: Changing Bank User...")

        self.nova.act("Click the Bank user field")
        time.sleep(1)

        self.nova.act(f"In the LEFTMOST column, click on '{bank}'")
        time.sleep(1)

        self.nova.act(f"In the MIDDLE column, click on '{region}'")
        time.sleep(1)

        self.nova.act(f"In the rightmost column, type '{branch}' in the search box, check the '{branch}' checkbox")
        time.sleep(1)

        self.nova.act("Click the purple 'Select' button to confirm the selection")
        time.sleep(1.5)

        logger.debug(f"Bank user updated to: {branch}")
        print(f"  ✅ Bank user updated to: {branch}")

    def _change_scope(self, bank: str, region: str, branch: str):
        """Change Scope with hierarchical selection and verification."""
        logger.debug("Changing Scope...")

        self.nova.act("In the FIRST row, click the Scope field")
        time.sleep(1)

        self.nova.act(f"In the LEFTMOST column, click on '{bank}'")
        time.sleep(1)

        self.nova.act(f"In the MIDDLE column, click on '{region}'")
        time.sleep(1)

        self.nova.act(f"In the rightmost column, type '{branch}' in the search box, check the '{branch}' checkbox")
        time.sleep(1)

        self.nova.act("Click the purple 'Select' button to confirm the selection")
        time.sleep(1.5)

        # Final verification: Check if selector closed and field shows correct value
        logger.debug("Verifying Scope field updated")
        try:
            result = self.nova.act_get(
                f"Look at the Scope field in the FIRST row. Does it now show the path with '{branch}' (like '... / {region} / {branch}' or similar)?",
                schema=BOOL_SCHEMA
            )
            if result.parsed_response:
                logger.debug(f"✓ Verification PASSED - Scope field updated")
                print(f"    ✓ Scope field updated with '{branch}'")
            else:
                raise Exception("Scope field should show selected branch path")
        except ActInvalidModelGenerationError as e:
            logger.error(f"Verification INVALID: {str(e)}")
            raise Exception(f"Failed to verify Scope field: {str(e)}")

        logger.debug(f"Scope updated to: {branch}")
        print(f"  ✅ Scope updated to: {branch}")
