"""
CSP Admin v2 - Simple wrapper approach
Handlers gốc GIỮ NGUYÊN, chỉ thêm wrapper layer
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.shared.nova_manager import NovaManager
from src.shared.logger import setup_automation_logger
from src.shared.screenshot_utils import ScreenshotManager
from src.shared.handler_wrapper import HandlerWrapper

# Import handlers GỐC - KHÔNG SỬA
from src.features.csp.handlers.csp_login_handler import CSPLoginHandler
from src.features.csp.handlers.csp_user_search_handler import CSPUserSearchHandler
from src.features.csp.handlers.csp_role_handler import CSPRoleHandler
from src.features.csp.handlers.csp_branch_handler import CSPBranchHandler
from src.features.csp.handlers.csp_save_handler import CSPSaveHandler

load_dotenv()


def process_user_simple(
    nova,
    admin_username: str,
    admin_password: str,
    target_user: str,
    new_role: str = None,
    branch_hierarchy: list = None,
    screenshot_manager = None,
    logger = None,
    execution_id: str = None
) -> dict:
    """
    Process user với wrapper approach
    Handlers gốc GIỮ NGUYÊN 100%
    """

    # Create wrapper
    wrapper = HandlerWrapper()

    logger.info(f"Processing user: {target_user}")
    print(f"\n{'='*60}")
    print(f"👤 Processing user: {target_user}")
    print(f"{'='*60}")

    result = {'success': False}

    try:
        # Step 1: Login (handler gốc)
        login_handler = CSPLoginHandler(nova, screenshot_manager=screenshot_manager)
        success = wrapper.execute_with_retry(
            step_name="login",
            handler_func=login_handler.login,
            max_retries=5,
            username=admin_username,
            password=admin_password
        )
        if not success:
            result['failed_steps'].append("login")
            return result

        # Step 2: Search user (handler gốc)
        search_handler = CSPUserSearchHandler(nova)
        success = wrapper.execute_with_retry(
            step_name="search_user",
            handler_func=search_handler.search_and_open_edit,
            max_retries=5,
            target_user=target_user
        )
        if not success:
            result['failed_steps'].append("search_user")
            return result

        # Screenshot after opening edit
        if screenshot_manager:
            screenshot_manager.capture(nova, step_name="edit_form_opened")

        # Step 3: Change role (handler gốc, optional)
        if new_role:
            role_handler = CSPRoleHandler(nova)
            success = wrapper.execute_with_retry(
                step_name="change_role",
                handler_func=role_handler.change_role,
                max_retries=5,
                new_role=new_role
            )
            if not success:
                result['failed_steps'].append("change_role")
                return result

        # Step 4: Change branch (handler gốc, optional)
        if branch_hierarchy:
            branch_handler = CSPBranchHandler(nova)
            success = wrapper.execute_with_retry(
                step_name="change_branch",
                handler_func=branch_handler.change_branch_hierarchical,
                max_retries=5,
                branch_hierarchy=branch_hierarchy
            )
            if not success:
                result['failed_steps'].append("change_branch")
                return result

        # Screenshot before save
        if screenshot_manager:
            screenshot_manager.capture(nova, step_name="before_save")

        # Step 5: Save changes (handler gốc)
        save_handler = CSPSaveHandler(nova)
        success = wrapper.execute_with_retry(
            step_name="save_changes",
            handler_func=save_handler.save_changes,
            max_retries=3
        )
        if not success:
            result['failed_steps'].append("save_changes")
            return result

        # Screenshot after save
        if screenshot_manager:
            screenshot_manager.capture(nova, step_name="after_save")

        # Success
        result['success'] = True
        logger.info(f"Successfully processed {target_user}")
        print(f"\n✅ Successfully processed {target_user}")

    except Exception as e:
        logger.error(f"Error processing {target_user}: {e}")
        print(f"\n❌ Error: {e}")

    return result


def main(
    input_file: str = None,
    url: str = None,
    execution_id: str = None
):
    """
    Main function - simple wrapper approach
    """

    # Generate execution ID
    if not execution_id:
        execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Setup logger
    logger = setup_automation_logger("csp_admin_simple_v2", execution_id)
    logger.info("Starting CSP Admin automation (simple wrapper approach)")
    print("🚀 CSP Admin Automation v2 - Simple Wrapper Approach")
    print("="*60)

    # Default input file
    if not input_file:
        input_file = Path(__file__).parent.parent.parent.parent / "input.json"

    # Load config
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
        user_id = user['target_user']
        user_execution_id = f"{execution_id}_user{i}_{user_id}"

        logger.info(f"Starting user {i}/{len(users)}: {user_id}")

        # Create screenshot manager
        screenshot_manager = ScreenshotManager(
            base_dir="screenshots",
            execution_id=user_execution_id
        )

        # Create Nova instance (reuse for retries)
        nova = None
        try:
            logger.info(f"Creating Nova session for {user_id}")
            nova = NovaManager.create_for_automation(
                automation_name="csp_admin",
                starting_page=admin_creds['csp_admin_url'],
                execution_id=user_execution_id
            )
            nova.start()
            logger.info("Nova session started")

            # Process user
            result = process_user_simple(
                nova=nova,
                admin_username=admin_creds['username'],
                admin_password=admin_creds['password'],
                target_user=user_id,
                new_role=user.get('new_role'),
                branch_hierarchy=user.get('branch_hierarchy'),
                screenshot_manager=screenshot_manager,
                logger=logger,
                execution_id=execution_id
            )

            # Check result
            if result['success']:
                success_count += 1
                logger.info(f"User {i}/{len(users)} completed successfully")
            else:
                logger.error(f"User {i}/{len(users)} failed")

        except Exception as e:
            logger.error(f"Error with user {user_id}: {e}")
            print(f"\n❌ Error: {e}")

        finally:
            # Stop Nova session
            if nova:
                try:
                    nova.stop()
                    logger.info("Nova session stopped")
                except:
                    pass

    # Summary
    logger.info("Automation completed")
    logger.info(f"Success: {success_count}/{len(users)}")
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"Total users: {len(users)}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {len(users) - success_count}")
    if len(users) > 0:
        print(f"Success rate: {(success_count/len(users)*100):.1f}%")
    print(f"\n🆔 Execution ID: {execution_id}")
    print(f"📂 Logs: logs/csp_admin_simple_v2/{execution_id}/")
    print(f"📸 Screenshots: screenshots/")
    print(f"{'='*60}")

    return success_count == len(users)


if __name__ == "__main__":
    import fire
    fire.Fire(main)
