import json
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from nova_act import NovaAct
from src.shared.logger import setup_automation_logger
from src.shared.screenshot_utils import ScreenshotManager
from src.shared.handler_wrapper import HandlerWrapper

from src.features.csp.handlers.csp_login_handler import CSPLoginHandler
from src.features.csp.handlers.csp_user_search_handler import CSPUserSearchHandler
from src.features.csp.handlers.csp_role_handler import CSPRoleHandler
from src.features.csp.handlers.csp_branch_handler import CSPBranchHandler
from src.features.csp.handlers.csp_save_handler import CSPSaveHandler

load_dotenv()


class UserProcessResult(BaseModel):
    """Model for user processing result"""
    user_id: str
    status: str  # "Success" or "Failed"
    error_message: str | None = None
    execution_time: float  # seconds
    failed_steps: list[str] = []


def process_single_user_parallel(
    admin_creds: dict,
    user_config: dict,
    execution_id: str,
    user_index: int = 1
) -> UserProcessResult:
    """
    Process a single user in parallel (headless mode).

    Args:
        admin_creds: Admin credentials dict
        user_config: User config dict with target_user, new_role, branch_hierarchy
        execution_id: Execution ID for logging
        user_index: User index for identification

    Returns:
        UserProcessResult object with processing status
    """
    user_id = user_config['target_user']
    user_execution_id = f"{execution_id}_user{user_index}_{user_id}"

    # Setup logger for this user
    logger = setup_automation_logger("csp_admin_parallel", user_execution_id)

    print(f"🔄 [Parallel] Processing user: {user_id}")
    logger.info(f"Starting parallel processing for user: {user_id}")

    start_time = time.time()

    # Get API key
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        raise ValueError("NOVA_ACT_API_KEY not found in .env file")

    # Create screenshot manager
    screenshot_manager = ScreenshotManager(
        base_dir="screenshots",
        execution_id=user_execution_id
    )

    result = {
        'success': False,
        'failed_steps': [],
        'user': user_id
    }

    try:
        # Create logs directory first
        logs_dir = f"logs/csp_admin_parallel/{user_execution_id}"
        Path(logs_dir).mkdir(parents=True, exist_ok=True)

        # Create Nova instance with context manager (headless for parallel)
        with NovaAct(
            starting_page=admin_creds['csp_admin_url'],
            headless=True,  # Always headless for parallel execution
            nova_act_api_key=api_key,
            ignore_https_errors=True,
            logs_directory=logs_dir
        ) as nova:

            wrapper = HandlerWrapper()
            has_changes = False

            # Step 1: Login
            login_handler = CSPLoginHandler(nova, screenshot_manager=screenshot_manager)
            success = wrapper.execute_with_retry(
                step_name="login",
                handler_func=login_handler.login,
                max_retries=3,
                username=admin_creds['username'],
                password=admin_creds['password']
            )
            if not success:
                result['failed_steps'].append("login")
                raise Exception("Login failed")

            # Step 2: Search user
            search_handler = CSPUserSearchHandler(nova)
            success = wrapper.execute_with_retry(
                step_name="search_user",
                handler_func=search_handler.search_and_open_edit,
                max_retries=3,
                target_user=user_id
            )
            if not success:
                result['failed_steps'].append("search_user")
                raise Exception("User search failed")

            # Screenshot after opening edit
            if screenshot_manager:
                screenshot_manager.capture(nova, step_name="edit_form_opened")

            # Step 3: Change role (optional)
            if user_config.get('new_role'):
                role_handler = CSPRoleHandler(nova)
                success = wrapper.execute_with_retry(
                    step_name="change_role",
                    handler_func=role_handler.change_role,
                    max_retries=3,
                    new_role=user_config['new_role']
                )
                if not success:
                    result['failed_steps'].append("change_role")
                    raise Exception("Role change failed")
                if role_handler.has_changes:
                    has_changes = True

            # Step 4: Change branch (optional)
            if user_config.get('branch_hierarchy'):
                branch_handler = CSPBranchHandler(nova)
                success = wrapper.execute_with_retry(
                    step_name="change_branch",
                    handler_func=branch_handler.change_branch_hierarchical,
                    max_retries=3,
                    branch_hierarchy=user_config['branch_hierarchy']
                )
                if not success:
                    result['failed_steps'].append("change_branch")
                    raise Exception("Branch change failed")
                if branch_handler.has_changes:
                    has_changes = True

            # Step 5: Save changes only if there were changes
            if has_changes:
                if screenshot_manager:
                    screenshot_manager.capture(nova, step_name="before_save")

                save_handler = CSPSaveHandler(nova)
                success = wrapper.execute_with_retry(
                    step_name="save_changes",
                    handler_func=save_handler.save_changes,
                    max_retries=3
                )
                if not success:
                    result['failed_steps'].append("save_changes")
                    raise Exception("Save failed")

                if screenshot_manager:
                    screenshot_manager.capture(nova, step_name="after_save")
            else:
                logger.info("No changes detected. Skipping save.")

            # Success
            result['success'] = True
            execution_time = time.time() - start_time

            logger.info(f"Successfully processed {user_id} in {execution_time:.1f}s")
            print(f"✅ [Parallel] Completed: {user_id} ({execution_time:.1f}s)")

            return UserProcessResult(
                user_id=user_id,
                status="Success",
                error_message=None,
                execution_time=execution_time,
                failed_steps=[]
            )

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)

        logger.error(f"Failed to process {user_id}: {error_msg}")
        print(f"❌ [Parallel] Failed: {user_id} - {error_msg}")

        return UserProcessResult(
            user_id=user_id,
            status="Failed",
            error_message=error_msg,
            execution_time=execution_time,
            failed_steps=result.get('failed_steps', [])
        )


def main(
    input_file: str = None,
    url: str = None,
    execution_id: str = None,
    max_workers: int = 3
):
    """
    Main function to run parallel CSP Admin automation.

    Processes multiple users concurrently using ThreadPoolExecutor.

    Args:
        input_file: Path to input.json file
        url: Override URL (optional)
        execution_id: Execution ID (auto-generated if not provided)
        max_workers: Maximum number of parallel workers (default: 3)

    Usage:
        # Basic parallel processing
        python src/features/csp/csp_admin_parallel.py

        # With custom max workers
        python src/features/csp/csp_admin_parallel.py --max_workers 5

        # With custom input file
        python src/features/csp/csp_admin_parallel.py --input_file custom_input.json
    """

    # Generate execution ID
    if not execution_id:
        execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Setup logger
    logger = setup_automation_logger("csp_admin_parallel", execution_id)
    logger.info("Starting CSP Admin Parallel automation")

    print("=" * 60)
    print("🚀 CSP ADMIN AUTOMATION - PARALLEL MODE")
    print("=" * 60)

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
    print(f"🔄 Max parallel workers: {max_workers}")
    print(f"🆔 Execution ID: {execution_id}")
    print("=" * 60)
    print()

    # Display user list
    print("📋 Users to process:")
    for i, user_config in enumerate(users, 1):
        target = user_config.get('target_user', 'Unknown')
        role = user_config.get('new_role', 'No change')
        branch = user_config.get('branch_hierarchy', [])
        branch_code = branch[-1] if branch else 'N/A'
        print(f"   {i}. {target} → Branch: {branch_code} | Role: {role}")
    print()

    # Execute parallel processing
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all user tasks
        future_to_user = {
            executor.submit(
                process_single_user_parallel,
                admin_creds,
                user_config,
                execution_id,
                i + 1
            ): user_config['target_user']
            for i, user_config in enumerate(users)
        }

        # Collect results as they complete
        print("⏳ Starting parallel processing...\n")
        for future in as_completed(future_to_user.keys()):
            result = future.result()
            if result is not None:
                results.append(result.model_dump())

    # Display results
    print("\n" + "=" * 60)
    print("📊 PARALLEL PROCESSING RESULTS")
    print("=" * 60)

    if results:
        results_df = pd.DataFrame(results)
        # Sort by status (Success first) then by execution time
        results_df = results_df.sort_values(by=['status', 'execution_time'], ascending=[False, True])

        print(f"\n{results_df.to_string()}\n")

        # Summary stats
        successful = len([r for r in results if r['status'] == 'Success'])
        failed = len(results) - successful
        total_time = sum(r['execution_time'] for r in results)
        avg_time = total_time / len(results)

        print("=" * 60)
        print("📈 STATISTICS")
        print("=" * 60)
        print(f"✅ Successful: {successful}/{len(results)}")
        print(f"❌ Failed: {failed}/{len(results)}")
        print(f"⏱️  Average time per user: {avg_time:.1f}s")
        print(f"⏱️  Total processing time: {total_time:.1f}s")
        print(f"🆔 Execution ID: {execution_id}")
        print(f"📂 Logs: logs/csp_admin_parallel/{execution_id}_user*/")
        print(f"📸 Screenshots: screenshots/")
        print("=" * 60)

        # Show failed users details
        if failed > 0:
            print("\n❌ FAILED USERS:")
            for r in results:
                if r['status'] == 'Failed':
                    print(f"   • {r['user_id']}: {r['error_message']}")
                    if r['failed_steps']:
                        print(f"     Failed steps: {', '.join(r['failed_steps'])}")
            print()
    else:
        print("❌ No results collected")

    logger.info("Parallel automation completed")
    logger.info(f"Results: {successful} success, {failed} failed")

    print("\n✨ Parallel processing completed!\n")

    return successful == len(results)


if __name__ == "__main__":
    import fire
    fire.Fire(main)
