from nova_act import NovaAct
from typing import List
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


class CSPBranchHandler:

    def __init__(self, nova: NovaAct):
        self.nova = nova
        self.action_counter = ActionCounter(max_actions=50, step_name="BranchChange")

    @with_retry(max_retries=2, retry_delay=2)
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

        # Open selector and navigate hierarchy
        self.action_counter.safe_act(
            self.nova,
            "Click the three dots button (...) next to the Bank user field"
        )
        time.sleep(1)

        # Wait for selector to open
        wait_for_loading_complete(
            self.nova,
            timeout_seconds=20,
            action_description="bank user selector to open"
        )

        self.action_counter.safe_act(
            self.nova,
            f"Click '{bank}' in the leftmost column, then click '{region}' in the middle column"
        )
        time.sleep(1)

        self.action_counter.safe_act(
            self.nova,
            f"Type '{branch}' in the search box in the rightmost column, "
            f"check and select the '{branch}' checkbox"
        )
        time.sleep(1)

        self.action_counter.safe_act(
            self.nova,
            "Click the purple 'Select button' to confirm bank user selection"
        )
        time.sleep(1)

        logger.debug(f"Bank user updated to: {branch}")
        print(f"✅ Bank user updated to: {branch}")

    def _change_scope(self, bank: str, region: str, branch: str):
        logger.debug("Changing Scope...")
        print("🎯 Step 2: Changing Scope...")

        # Open selector and navigate hierarchy
        self.action_counter.safe_act(
            self.nova,
            "Click the Scope input field which already have delete button to open the scope selector"
        )
        time.sleep(1)

        # Wait for selector to open
        wait_for_loading_complete(
            self.nova,
            timeout_seconds=20,
            action_description="scope selector to open"
        )

        self.action_counter.safe_act(
            self.nova,
            f"Click '{bank}' in the leftmost column, then click '{region}' in the middle column"
        )
        time.sleep(1)

        self.action_counter.safe_act(
            self.nova,
            f"Type '{branch}' in the search box in the rightmost column, "
            f"check and select the '{branch}' checkbox"
        )
        time.sleep(1)

        self.action_counter.safe_act(
            self.nova,
            "Click the purple 'Select button'"
        )
        time.sleep(1)

        logger.debug(f"Scope updated to: {branch}")
        print(f"✅ Scope updated to: {branch}")
