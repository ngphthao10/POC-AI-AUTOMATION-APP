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

    wrapper = HandlerWrapper()

    logger.info(f"Processing user: {target_user}")
    print(f"\n{'='*60}")
    print(f"👤 Processing user: {target_user}")
    print(f"{'='*60}")

    result = {'success': False}

    try:
        # Step 1: Login
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

        # Step 2: Search user
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

        # Step 3: Change role (optional)
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

        # Step 4: Change branch (optional)
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

        # Step 5: Save changes 
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


def process_single_user(
    admin_creds: dict,
    user_config: dict,
    execution_id: str,
    logger,
    user_index: int = 1
) -> dict:
    """Process a single user and return result"""
    user_id = user_config['target_user']
    user_execution_id = f"{execution_id}_user{user_index}_{user_id}"

    logger.info(f"Starting user: {user_id}")

    # Create screenshot manager
    screenshot_manager = ScreenshotManager(
        base_dir="screenshots",
        execution_id=user_execution_id
    )

    # Create Nova instance
    nova = None
    result = {'success': False, 'user': user_id}

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
            new_role=user_config.get('new_role'),
            branch_hierarchy=user_config.get('branch_hierarchy'),
            screenshot_manager=screenshot_manager,
            logger=logger,
            execution_id=execution_id
        )
        result['user'] = user_id

    except Exception as e:
        logger.error(f"Error with user {user_id}: {e}")
        print(f"\n❌ Error: {e}")
        result['success'] = False
        result['error'] = str(e)

    finally:
        # Stop Nova session
        if nova:
            try:
                nova.stop()
                logger.info("Nova session stopped")
            except:
                pass

    return result


def main(
    input_file: str = None,
    url: str = None,
    execution_id: str = None
):
    # Generate execution ID
    if not execution_id:
        execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Setup logger
    logger = setup_automation_logger("csp_admin", execution_id)
    logger.info("Starting CSP Admin automation")
    print("🚀 CSP Admin Automation - Interactive Mode")
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
    logger.info(f"Loaded {len(users)} users from config")
    print(f"🌐 Target URL: {admin_creds['csp_admin_url']}")
    print(f"👥 Loaded {len(users)} user(s) from config")
    print(f"🆔 Execution ID: {execution_id}")

    # Statistics
    success_count = 0
    failed_count = 0
    total_processed = 0
    current_user_index = 0

    # Main interactive loop - process users from list
    while current_user_index < len(users):
        user_config = users[current_user_index]
        print(f"\n{'='*60}")
        print(f"🔄 User {current_user_index + 1}/{len(users)}: {user_config['target_user']}")
        print(f"{'='*60}")

        # Retry loop for current user
        while True:
            result = process_single_user(
                admin_creds=admin_creds,
                user_config=user_config,
                execution_id=execution_id,
                logger=logger,
                user_index=current_user_index + 1
            )

            if result['success']:
                success_count += 1
                total_processed += 1
                logger.info(f"User {result['user']} completed successfully")
                print(f"\n✅ Thành công! User {result['user']} đã được xử lý.")

                # Move to next user
                current_user_index += 1

                # Ask if continue to next user
                if current_user_index < len(users):
                    continue_choice = input(f"\nTiếp tục xử lý user tiếp theo? (y/n): ").strip().lower()
                    if continue_choice != 'y':
                        print("\n🛑 Dừng xử lý theo yêu cầu.")
                        break
                break
            else:
                logger.error(f"User {result['user']} failed")
                print(f"\n❌ Thất bại! User {result['user']} xử lý không thành công.")

                # Ask if retry
                retry = input("\n🔄 Thử lại user này? (y/n): ").strip().lower()
                if retry == 'y':
                    print("\n🔄 Đang thử lại...")
                    continue
                else:
                    # Don't retry, move to next
                    failed_count += 1
                    total_processed += 1
                    current_user_index += 1

                    # Ask if continue to next user
                    if current_user_index < len(users):
                        continue_choice = input(f"\nTiếp tục xử lý user tiếp theo? (y/n): ").strip().lower()
                        if continue_choice != 'y':
                            print("\n🛑 Dừng xử lý theo yêu cầu.")
                            break
                    break

        # Check if user wants to stop
        if current_user_index < len(users):
            # Check from last continue_choice
            if 'continue_choice' in locals() and continue_choice != 'y':
                break

    # Final summary
    print(f"\n{'='*60}")
    print("📊 TỔNG KẾT")
    print(f"{'='*60}")
    print(f"Tổng users trong file: {len(users)}")
    print(f"Đã xử lý: {total_processed}")
    print(f"✅ Thành công: {success_count}")
    print(f"❌ Thất bại: {failed_count}")
    if total_processed > 0:
        print(f"Tỷ lệ thành công: {(success_count/total_processed*100):.1f}%")
    print(f"\n🆔 Execution ID: {execution_id}")
    print(f"📂 Logs: logs/csp_admin/{execution_id}/")
    print(f"📸 Screenshots: screenshots/")
    print(f"{'='*60}")

    logger.info("Automation completed")
    logger.info(f"Total processed: {total_processed}, Success: {success_count}, Failed: {failed_count}")

    return success_count == total_processed


if __name__ == "__main__":
    import fire
    fire.Fire(main)
