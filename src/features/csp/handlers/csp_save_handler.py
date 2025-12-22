from nova_act import NovaAct
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.logger import setup_logger
from shared.retry_utils import with_retry
from shared.wait_utils import wait_for_loading_complete
from shared.error_utils import format_error_for_display

logger = setup_logger(__name__)


class CSPSaveHandler:

    def __init__(self, nova: NovaAct):
        self.nova = nova

    @with_retry(max_retries=2, retry_delay=2)
    def save_changes(self) -> bool:
        """Save changes and wait for completion"""
        try:
            logger.info("Saving changes...")
            print("💾 Saving changes...")

            self.nova.act("Click the green 'Save' button")
            time.sleep(1)

            # Wait for save operation to complete
            if not wait_for_loading_complete(
                self.nova,
                timeout_seconds=60,
                action_description="save operation to complete"
            ):
                raise Exception("Save operation timeout")

            logger.info("Changes saved successfully")
            print("✅ Changes saved successfully")
            return True

        except Exception as e:
            logger.error(f"Save failed: {str(e)}")
            error_msg = format_error_for_display(e, context="Save")
            print(error_msg)
            raise

    def close_modal(self) -> bool:
        """Close edit modal without saving"""
        try:
            logger.info("Closing modal...")
            print("🚪 Closing modal...")

            self.nova.act("Click the Cancel button or X button to close the modal")
            time.sleep(1)

            logger.info("Modal closed")
            return True

        except Exception as e:
            logger.error(f"Close modal failed: {str(e)}")
            return False
