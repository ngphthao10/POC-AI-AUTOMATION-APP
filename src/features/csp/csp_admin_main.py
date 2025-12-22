import json
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.nova_manager import NovaManager
from shared.logger import setup_automation_logger
from shared.screenshot_utils import ScreenshotManager
from shared.error_utils import format_error_for_display

from features.csp.handlers.csp_login_handler import CSPLoginHandler
from features.csp.handlers.csp_user_search_handler import CSPUserSearchHandler
from features.csp.handlers.csp_role_handler import CSPRoleHandler
from features.csp.handlers.csp_branch_handler import CSPBranchHandler
from features.csp.handlers.csp_save_handler import CSPSaveHandler

load_dotenv()


def process_user(
    nova,
    admin_username: str,
    admin_password: str,
    target_user: str,
    new_role: str = None,
    branch_hierarchy: list = None,
    screenshot_manager: ScreenshotManager = None,
    logger = None
) -> bool:
    """Process a single user with enhanced error handling and logging"""

    logger.info(f"Processing user: {target_user}")
    print(f"\n{'='*60}")
    print(f"👤 Processing user: {target_user}")
    print(f"{'='*60}")

    try:
        # 1. Login
        login_handler = CSPLoginHandler(nova, screenshot_manager=screenshot_manager)
        if not login_handler.login(admin_username, admin_password):
            logger.error(f"Login failed for {target_user}")
            return False

        # 2. Search and open edit
        search_handler = CSPUserSearchHandler(nova)
        if not search_handler.search_and_open_edit(target_user):
            logger.error(f"User search failed for {target_user}")
            return False

        # Take screenshot after opening edit form
        if screenshot_manager:
            screenshot_manager.capture(nova, step_name="edit_form_opened")

        # 3. Change role (if requested)
        if new_role:
            role_handler = CSPRoleHandler(nova)
            if not role_handler.change_role(new_role):
                logger.error(f"Role change failed for {target_user}")
                return False

        # 4. Change branch (if requested)
        if branch_hierarchy:
            branch_handler = CSPBranchHandler(nova)
            if not branch_handler.change_branch_hierarchical(branch_hierarchy):
                logger.error(f"Branch change failed for {target_user}")
                return False

        # Take screenshot before saving
        if screenshot_manager:
            screenshot_manager.capture(nova, step_name="before_save")

        # 5. Save changes
        save_handler = CSPSaveHandler(nova)
        if not save_handler.save_changes():
            logger.error(f"Save failed for {target_user}")
            return False

        # Take screenshot after saving
        if screenshot_manager:
            screenshot_manager.capture(nova, step_name="after_save")

        logger.info(f"Successfully processed {target_user}")
        print(f"\n✅ Successfully processed {target_user}")
        return True

    except Exception as e:
        logger.error(f"Error processing {target_user}: {str(e)}")
        error_msg = format_error_for_display(e, context=f"Processing {target_user}")
        print(error_msg)

        # Screenshot on error
        if screenshot_manager:
            from shared.screenshot_utils import capture_screenshot_on_error
            capture_screenshot_on_error(
                nova, e,
                base_dir=screenshot_manager.get_screenshot_dir()
            )

        return False


def main(
    input_file: str = None,
    url: str = None,
    headless: bool = None
):
    """
    Main entry point with enhanced features

    Args:
        input_file: Path to input JSON file
        url: CSP portal URL (optional, reads from input file)
        headless: Run in headless mode (reads from .env if not specified)
    """
    # Generate execution ID
    execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Setup logger
    logger = setup_automation_logger("csp_admin", execution_id)
    logger.info("Starting CSP Admin automation")

    # Default input file
    if not input_file:
        input_file = Path(__file__).parent.parent.parent.parent / "input.json"

    # Load input config
    logger.info(f"Loading config from: {input_file}")
    print(f"📂 Loading config from: {input_file}")

    with open(input_file) as f:
        config = json.load(f)

    admin_creds = config['admin_credentials']
    users = config['users']

    # Override URL if provided
    if url:
        admin_creds['csp_admin_url'] = url

    logger.info(f"Target URL: {admin_creds['csp_admin_url']}")
    logger.info(f"Processing {len(users)} users")
    print(f"🌐 Target URL: {admin_creds['csp_admin_url']}")
    print(f"👥 Processing {len(users)} user(s)")
    print(f"🆔 Execution ID: {execution_id}")
    print()

    # Process each user
    success_count = 0
    for i, user in enumerate(users, 1):
        user_execution_id = f"{execution_id}_user{i}_{user['target_user']}"
        logger.info(f"Starting user {i}/{len(users)}: {user['target_user']}")

        # Create screenshot manager for this user
        screenshot_manager = ScreenshotManager(
            base_dir="screenshots",
            execution_id=user_execution_id
        )

        # Create Nova Act instance with enhanced features
        nova = NovaManager.create_for_automation(
            automation_name="csp_admin",
            starting_page=admin_creds['csp_admin_url'],
            execution_id=user_execution_id
        )

        try:
            # Start Nova session
            nova.start()
            logger.info(f"Nova session started for {user['target_user']}")

            # Process user
            success = process_user(
                nova=nova,
                admin_username=admin_creds['username'],
                admin_password=admin_creds['password'],
                target_user=user['target_user'],
                new_role=user.get('new_role'),
                branch_hierarchy=user.get('branch_hierarchy'),
                screenshot_manager=screenshot_manager,
                logger=logger
            )

            if success:
                success_count += 1
                logger.info(f"User {i}/{len(users)} completed successfully")
            else:
                logger.error(f"User {i}/{len(users)} failed")

        except Exception as e:
            logger.error(f"Error with user {user['target_user']}: {str(e)}")
            error_msg = format_error_for_display(e, context=f"User {user['target_user']}")
            print(error_msg)

        finally:
            # Stop Nova session
            try:
                nova.stop()
                logger.info(f"Nova session stopped for {user['target_user']}")
            except:
                pass

    # Summary
    logger.info("Automation completed")
    logger.info(f"Success rate: {success_count}/{len(users)}")
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"Total users: {len(users)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(users) - success_count}")
    print(f"Success rate: {(success_count/len(users)*100):.1f}%")
    print(f"Execution ID: {execution_id}")
    print(f"📂 Logs: logs/csp_admin/")
    print(f"📸 Screenshots: screenshots/")
    print(f"{'='*60}")

    return success_count == len(users)


if __name__ == "__main__":
    import fire
    fire.Fire(main)
