"""
CSP Admin Change Role and Branch Automation

This automation handles the process of changing user roles and branch assignments 
in CSP web applications for IT support teams using hierarchical branch navigation.

Usage:
python -m src.csp.csp_admin_change_role_and_branch --input_file src/csp/input.json [--per_user_session False]

Note: The app now runs in single worker mode by default for improved stability and reliability.
Previous parallel worker support has been removed to prevent potential issues with concurrent browser sessions.

Input JSON format:
{
    "admin_credentials": {
        "username": "admin_user",
        "password": "admin_password",
        "csp_admin_url": "https://your-csp-admin-portal.com"
    },
    "users": [
        {
            "target_user": "user1@example.com",
            "new_role": "manager",
            "branch_hierarchy": ["VIB Bank", "North", "001_HA NOI"]
        },
        {
            "target_user": "user2@example.com", 
            "new_role": "employee",
            "branch_hierarchy": ["VIB Bank", "South", "002_HO CHI MINH"]
        }
    ]
}

Branch Hierarchy Support:
- The automation uses hierarchical navigation for all branch changes
- 'branch_hierarchy' should be provided as an array representing the hierarchical path
- Each element in the array represents a level in the hierarchy (e.g., Bank → Region → Branch)
- The final element in the hierarchy is considered the target branch
- For backward compatibility, 'new_branch' can still be used, but it will be converted to a default hierarchy
- This supports complex organizational structures where branches are nested under regions or departments
"""

import getpass
import time
import json
import fire
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict
from pydantic import BaseModel

from nova_act import NovaAct, BOOL_SCHEMA
from nova_act.types.errors import StartFailed

# Configure logging at the module level
def setup_logging():
    """Setup comprehensive logging for the automation following Nova Act best practices"""
    # Set Nova Act log level to DEBUG (integer value as per Nova Act documentation)
    os.environ['NOVA_ACT_LOG_LEVEL'] = '10'  # 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR
    
    # Configure Python logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler(f'csp_automation_{int(time.time())}.log')  # File output
        ]
    )
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Debug logging enabled for CSP automation")
    logger.info("Nova Act will generate HTML trace files with step-by-step actions")
    return logger

# Initialize logging
logger = setup_logging()

# Import Nova Act configuration
try:
    from src.config.nova_act_config import get_nova_act_api_key
except ImportError:
    # Fallback for development/non-built environments
    def get_nova_act_api_key():
        import os
        api_key = os.getenv('NOVA_ACT_API_KEY')
        if not api_key:
            raise ValueError(
                "Nova Act API key not found. Please set NOVA_ACT_API_KEY environment variable "
                "or configure it in src/config/nova_act_config.py"
            )
        return api_key


class AdminCredentials(BaseModel):
    """Schema for admin credentials"""
    username: str
    password: str
    csp_admin_url: str


class UserChangeRequest(BaseModel):
    """Schema for individual user change request"""
    target_user: str
    new_role: Optional[str] = None
    new_branch: Optional[str] = None
    branch_hierarchy: Optional[List[str]] = None


class InputConfig(BaseModel):
    """Schema for complete input configuration"""
    admin_credentials: AdminCredentials
    users: List[UserChangeRequest]


class RoleChangeResult(BaseModel):
    """Schema for role change operation results"""
    user_email: str
    new_role: str
    new_branch: str
    status: str
    timestamp: str


class CSPAdminRoleAndBranchChanger:
    """Automate CSP admin role and branch change operations"""
    
    def __init__(self, csp_admin_url: str, nova_act_api_key: str = None, logs_directory: str = None):
        self.csp_admin_url = csp_admin_url
        self.nova_act_api_key = nova_act_api_key
        self.session_data = {}
        self.results: List[RoleChangeResult] = []
        
        # Setup logs directory for Nova Act traces
        if not logs_directory:
            self.logs_directory = f"./logs/csp_automation_{int(time.time())}"
        else:
            self.logs_directory = logs_directory
        
        # Create logs directory
        Path(self.logs_directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Nova Act traces will be saved to: {self.logs_directory}")
        logger.info("Nova Act will automatically generate:")
        logger.info("- HTML trace files with step-by-step screenshots")
        logger.info("- Video recordings of browser sessions (if record_video=True)")
        logger.info("- Detailed action logs for debugging")
    
    def wait_for_loading_complete(self, nova: NovaAct, timeout_seconds: int = 60, action_description: str = "page to load") -> bool:
        """
        Wait for loading indicators to disappear with timeout handling.
        This method only observes the page state and does NOT perform any clicks or actions.
        
        Args:
            nova: NovaAct instance
            timeout_seconds: Maximum time to wait for loading to complete (default 60 seconds)
            action_description: Description of what we're waiting for (for logging)
            
        Returns:
            bool: True if loading completed within timeout, False if timeout occurred
        """
        start_time = time.time()
        logger.debug(f"Waiting for {action_description} (timeout: {timeout_seconds}s)")
        print(f"⏳ Waiting for {action_description}...")
        
        while time.time() - start_time < timeout_seconds:
            # Check for common loading indicators - OBSERVATION ONLY, NO ACTIONS
            is_loading = nova.act(
                "OBSERVE ONLY: Check if there are any loading indicators currently visible on the page: loading spinner, 'Loading...' text, progress bars, or modal dialogs with spinning wheels. Return True if any loading indicators are visible, False if page appears fully loaded. DO NOT click anything.",
                schema=BOOL_SCHEMA
            )
            
            if is_loading.matches_schema and not is_loading.parsed_response:
                # No loading indicators found - page is ready
                elapsed = time.time() - start_time
                logger.debug(f"Loading completed after {elapsed:.1f} seconds")
                print(f"✅ {action_description.title()} completed ({elapsed:.1f}s)")
                return True
            
            # Brief pause before checking again
            time.sleep(2)
            elapsed = time.time() - start_time
            if elapsed % 10 == 0:  # Log progress every 10 seconds
                logger.debug(f"Still waiting for {action_description} ({elapsed:.0f}s elapsed)")
                print(f"⏳ Still waiting for {action_description} ({elapsed:.0f}s elapsed)")
        
        # Timeout occurred
        elapsed = time.time() - start_time
        logger.error(f"Timeout waiting for {action_description} after {elapsed:.1f} seconds")
        print(f"❌ Timeout: {action_description} did not complete within {timeout_seconds} seconds")
        return False
    
    def create_nova_act_instance(self, starting_page: str, **kwargs) -> NovaAct:
        """Create NovaAct instance with debug logging enabled following Nova Act best practices"""
        logger.debug(f"Creating Nova Act instance for: {starting_page}")
        logger.debug(f"Logs directory: {self.logs_directory}")
        
        return NovaAct(
            starting_page=starting_page,
            headless=False,
            ignore_https_errors=True,
            nova_act_api_key=self.nova_act_api_key,
            logs_directory=self.logs_directory,  # Nova Act will create HTML trace files here
            record_video=True,  # Enable video recording as per Nova Act README
            **kwargs
        )
    
    def load_input_config(self, input_file: str) -> InputConfig:
        """Load and validate input configuration from JSON file"""
        logger.debug(f"Loading input configuration from: {input_file}")
        try:
            input_path = Path(input_file)
            if not input_path.exists():
                logger.error(f"Input file not found: {input_file}")
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            logger.debug("Reading JSON file")
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug("Validating configuration structure")
            config = InputConfig.model_validate(data)
            logger.info(f"Successfully loaded configuration for {len(config.users)} users")
            print(f"✅ Loaded configuration for {len(config.users)} users")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {input_file}: {e}")
            raise ValueError(f"Invalid JSON format in {input_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading input file {input_file}: {e}")
            raise ValueError(f"Error loading input file {input_file}: {e}")
    
    def save_results(self, output_file: str = None):
        """Save automation results to JSON file"""
        if not output_file:
            output_file = f"csp_admin_results_{int(time.time())}.json"
        
        results_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_users": len(self.results),
            "successful": len([r for r in self.results if r.status.startswith("success")]),
            # treat any status beginning with 'failed' as failure (allows richer failure messages)
            "failed": len([r for r in self.results if r.status.startswith("failed")]),
            "results": [result.model_dump() for result in self.results]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Results saved to: {output_file}")
    
    def login(self, nova: NovaAct, username: str, password: str) -> bool:
        """Handle admin login process following Nova Act best practices"""
        logger.debug(f"Starting login process for user: {username}")
        print(f"🔐 Logging into VIB Portal as: {username}")
        
        # Enter username with Unicode encoding for special characters
        logger.debug("Locating username field")
        nova.act("Find and click the username field")
        # unicode_username = username.encode('unicode_escape').decode('ascii')
        username_field = nova.page.locator('input').first
        username_field.clear()
        username_field.type(username)
        logger.debug(f"Username entered: {username}")
        
        # Enter password
        logger.debug("Locating password field")
        nova.act("Find and click the password field")
        nova.page.keyboard.type(password)
        logger.debug("Password entered")
        
        # Step 3: Submit login form
        logger.debug("Submitting login form")
        nova.act("Click the login button to sign in")
        
        # Step 4: Wait briefly for page transition
        time.sleep(2)
        
        # Step 5: Verify successful login with specific elements from the screenshot
        logger.debug("Verifying login success")
        login_success = nova.act(
            "Check if successfully logged in by looking for: the 'BPC CUSTOMER SERVICE PORTAL' header, left navigation menu with 'Administration' section, and user name displayed in top right corner", 
            schema=BOOL_SCHEMA
        )
        
        if login_success.matches_schema and login_success.parsed_response:
            logger.info("Login successful - portal interface loaded")
            print("✅ Login successful - portal interface loaded!")
            return True
        else:
            # Check for specific login error indicators
            logger.debug("Checking for login error messages")
            error_present = nova.act(
                "Check if there are any error messages, invalid credentials alerts, or if still on login page",
                schema=BOOL_SCHEMA
            )
            
            if error_present.matches_schema and error_present.parsed_response:
                logger.error("Login failed - error message or still on login page")
                print("❌ Login failed - invalid credentials or login error")
            else:
                logger.error("Login status unclear - unexpected page state")
                print("❌ Login status unclear - unexpected page state")
            return False
    
    def navigate_to_user_management(self, nova: NovaAct) -> bool:
        """Navigate to user management section"""
        logger.debug("Starting navigation to user management")
        print("🧭 Navigating to user management...")
        
        # Check if already on users page
        logger.debug("Checking if already on user management page")
        already_on_users = nova.act("Check if we can see a user management table with columns like ID, Login, Name, Scope", 
                                   schema=BOOL_SCHEMA)
        
        if already_on_users.matches_schema and already_on_users.parsed_response:
            logger.info("Already on user management page")
            print("✅ Already on user management page")
            return True
        
        # Navigate: Administration → Users
        logger.debug("Navigating through Administration → Users")
        nova.act("Click on Administration in the left navigation")
        nova.act("Click on Users under Administration")
        time.sleep(2)
        
        # Verify we reached the users page
        logger.debug("Verifying successful navigation to user management")
        success = nova.act("Check if we can see the user management interface with search fields and user table", 
                          schema=BOOL_SCHEMA)
        
        if success.matches_schema and success.parsed_response:
            logger.info("Successfully navigated to user management")
            print("✅ Successfully navigated to user management")
            return True
        else:
            logger.error("Failed to navigate to user management")
            print("❌ Failed to navigate to user management")
            return False
    
    def search_user(self, nova: NovaAct, target_user: str) -> bool:
        """Search for target user and open edit form with optimized reliability"""
        logger.debug(f"Starting user search for: {target_user}")
        print(f"🔍 Searching for user: {target_user}")
        
        # Step 1: Check if advanced filters are already expanded
        logger.debug("Checking if search filters are already expanded")
        filters_expanded = nova.act(
            "Check if detailed search filters are visible (ID field, Login field, Scope dropdown, Block status dropdown). Return True if all filter fields are visible, False if only basic search is shown",
            schema=BOOL_SCHEMA
        )
        
        # Step 2: Expand filters if needed
        if not (filters_expanded.matches_schema and filters_expanded.parsed_response):
            logger.debug("Expanding search filters")
            nova.act("Click the 'More filters' button next to the search fields to expand the detailed filter options")
            time.sleep(1)
            
            # Verify filters expanded successfully
            filters_check = nova.act(
                "Verify that detailed filter fields are now visible (ID, Login, Scope, Block status fields)",
                schema=BOOL_SCHEMA
            )
            if not (filters_check.matches_schema and filters_check.parsed_response):
                logger.error("Failed to expand search filters")
                print("❌ Failed to expand search filters")
                return False
        else:
            logger.debug("Search filters already expanded")
            print("✅ Search filters already expanded")
        
        # Step 3: Clear and enter search term in Login field
        logger.debug(f"Clearing and entering search term: {target_user}")
        nova.act("Click on the Login field to focus it")
        nova.act("Clear all text from the Login field (select all and delete if needed)")
        nova.act(f"Type '{target_user}' in the Login field")
        
        # Step 4: Perform search
        logger.debug("Performing search")
        nova.act("Click the purple 'Search' button to execute the search")
        
        # Wait for search results to load
        if not self.wait_for_loading_complete(nova, timeout_seconds=60, action_description="search results to load"):
            logger.error("Search operation timeout")
            print("❌ Search operation timeout")
            return False
        
        # Step 5: Verify search was executed and check results
        logger.debug("Verifying search execution and checking for results")
        search_executed = nova.act(
            "Check if the search has been executed by looking for either user results in the table or a 'no records found' message",
            schema=BOOL_SCHEMA
        )
        
        if not (search_executed.matches_schema and search_executed.parsed_response):
            logger.error("Search does not appear to have been executed")
            print("❌ Search execution failed")
            return False
        
        # Step 6: Check for no results
        no_records = nova.act(
            "Check if 'no records found' message is displayed or if the table is empty with no user rows",
            schema=BOOL_SCHEMA
        )
        if no_records.matches_schema and no_records.parsed_response:
            logger.warning(f"No records found for user: {target_user}")
            print(f"❌ No records found for user: {target_user}")
            return False
        
        # Step 7: Verify target user row exists (accounting for domain prefixes)
        logger.debug(f"Verifying user row exists for: {target_user}")
        row_present = nova.act(
            f"Check that a table row exists where the Login cell contains '{target_user}' as a substring (the login might be in format like 'domain\\{target_user}' or 'prefix\\{target_user}'). Case-insensitive substring match is acceptable.",
            schema=BOOL_SCHEMA
        )
        if not (row_present.matches_schema and row_present.parsed_response):
            logger.error(f"Could not find row for user: {target_user}")
            print(f"❌ Could not find row for user: {target_user}")
            # Additional debugging - extract what was actually found
            found_users = nova.act("List all login values visible in the current search results table")
            logger.debug(f"Available users in search results: {found_users.response}")
            return False
        
        logger.info(f"Successfully found user: {target_user}")
        print(f"✅ Found user: {target_user}")

        # Step 8: Open edit modal with improved reliability
        return self._open_edit_modal(nova, target_user)
    
    def _open_edit_modal(self, nova: NovaAct, target_user: str) -> bool:
        """Helper method to open edit modal for a specific user with retry logic"""
        logger.debug(f"Opening edit modal for user: {target_user}")
        
        for attempt in range(1, 4):  # Up to 3 attempts
            if attempt > 1:
                logger.debug(f"Retrying edit modal open (attempt {attempt})")
                print(f"↻ Retrying opening Edit modal (attempt {attempt})")
                time.sleep(1)
                
                # Close any existing dropdown before retrying
                nova.act("Click elsewhere on the page to close any open dropdown menus")
                time.sleep(0.5)
            
            try:
                # Step 1: Open actions dropdown for the specific user row (improved substring matching)
                logger.debug("Opening actions dropdown")
                nova.act(
                    f"In the table, find the row where the Login column contains '{target_user}' as a substring (it may be formatted like 'domain\\{target_user}' or 'prefix\\{target_user}'). Click the 'Select' dropdown button in the Actions column for that specific row."
                )
                time.sleep(1)
                
                # Step 2: Verify dropdown opened with specific menu items
                logger.debug("Verifying dropdown menu opened")
                dropdown_open = nova.act(
                    "Check if a dropdown menu is now visible showing exactly these three options: 'View details', 'Edit', and 'Manage authentication'",
                    schema=BOOL_SCHEMA
                )
                
                if not (dropdown_open.matches_schema and dropdown_open.parsed_response):
                    logger.warning(f"Actions dropdown did not open properly on attempt {attempt}")
                    # Try to identify what's actually visible for debugging
                    visible_elements = nova.act("Describe what is currently visible on the screen after attempting to open the dropdown")
                    logger.debug(f"Current screen state: {visible_elements.response}")
                    continue
                
                # Step 3: Click the Edit option specifically
                logger.debug("Clicking Edit menu item")
                nova.act(
                    "In the opened dropdown menu, click exactly on the 'Edit' option. Do NOT click 'View details' or 'Manage authentication'"
                )
                time.sleep(1.5)
                
                # Step 4: Verify edit modal/form opened
                logger.debug("Verifying edit modal opened")
                edit_loaded = nova.act(
                    "Check if an edit user modal or form is now displayed. Look for a modal dialog containing user editing fields, tabs like 'General' and 'Roles', or form inputs for user management",
                    schema=BOOL_SCHEMA
                )
                
                if edit_loaded.matches_schema and edit_loaded.parsed_response:
                    logger.debug("Edit modal opened, waiting for loading to complete")
                    # Wait for any loading indicators to disappear
                    if self.wait_for_loading_complete(nova, timeout_seconds=60, action_description="edit modal to fully load"):
                        logger.info(f"Edit form loaded successfully for user: {target_user}")
                        print(f"✅ Edit form loaded for user {target_user}")
                        return True
                    else:
                        logger.error(f"Edit modal loading timeout for user: {target_user}")
                        print(f"❌ Edit modal loading timeout for user: {target_user}")
                        return False
                else:
                    logger.warning(f"Edit modal did not open on attempt {attempt}")
                    
                    # Additional check: verify we're not still on the user list
                    still_on_list = nova.act(
                        "Check if we're still looking at the user management table (with columns ID, Login, Name, etc.)",
                        schema=BOOL_SCHEMA
                    )
                    if still_on_list.matches_schema and still_on_list.parsed_response:
                        logger.warning("Still on user list - Edit action may not have worked")
                        # Extract the actual login value for debugging
                        actual_login = nova.act(f"In the table, find the row containing '{target_user}' and extract the exact text from its Login column")
                        logger.debug(f"Actual login value found: {actual_login.response}")
                    
            except Exception as e:
                logger.warning(f"Exception on attempt {attempt}: {str(e)}")
                continue
        
        logger.error(f"Failed to load edit form for {target_user} after {attempt} attempts")
        print(f"❌ Failed to load edit form for {target_user} after all attempts")
        return False
    
    def change_user_role(self, nova: NovaAct, new_role: str) -> bool:
        """Change user role using the Roles tab in the Edit user modal"""
        logger.debug(f"Starting role change to: {new_role}")
        print(f"👤 Changing user role to: {new_role}")
        
        # Step 1: Navigate to Roles tab (modal opens on Person tab by default)
        logger.debug("Navigating to Roles tab")
        nova.act("In the Edit user modal, click on the 'Roles' tab to switch from the default Person tab")
        time.sleep(1)
        
        # Step 2: Verify we're on the Roles tab
        logger.debug("Verifying Roles tab is active")
        on_roles_tab = nova.act(
            "Check if the 'Roles' tab is currently active/highlighted and role-related fields (Role, Scope, User category) are visible",
            schema=BOOL_SCHEMA
        )
        
        if not (on_roles_tab.matches_schema and on_roles_tab.parsed_response):
            logger.error("Failed to navigate to Roles tab")
            print("❌ Failed to navigate to Roles tab")
            return False
        
        logger.debug("Successfully on Roles tab")
        print("✅ Successfully navigated to Roles tab")
        
        # Step 3: Check if role already matches
        logger.debug(f"Checking if role already matches: {new_role}")
        pre_match = nova.act(
            f"Look at the Role field (not the 'Select role...' dropdown) and check if it currently shows '{new_role}' exactly",
            schema=BOOL_SCHEMA
        )
        
        # If role already matches, return early
        if pre_match.matches_schema and pre_match.parsed_response:
            logger.info(f"Role already set to '{new_role}' - no change needed")
            print(f"ℹ️ Role already set to '{new_role}' - no change needed")
            self.session_data['last_role_change_performed'] = False
            return True
        
        # Step 4: Clear existing role and set new role
        logger.debug(f"Updating role field to: {new_role}")
        nova.act("Click the X button next to the current role to clear it")
        time.sleep(0.5)
        
        # Step 5: Use the 'Select role...' dropdown to search and choose new role
        nova.act("Click on the 'Select role...' dropdown to open the role selection list")
        time.sleep(1)
        
        # Use search functionality in the dropdown and click the result to populate
        nova.act(f"Click on the 'Select role...' input field and type '{new_role}' to search for the role. Then click on the '{new_role}' option that appears in the filtered dropdown results to populate the role field")
        time.sleep(2)  # Allow time for the selection to populate
        
        # Verify the role was populated in the dropdown
        role_populated = nova.act(
            f"Check if the role dropdown now shows '{new_role}' as the selected value (not just in the search results)",
            schema=BOOL_SCHEMA
        )
        
        if not (role_populated.matches_schema and role_populated.parsed_response):
            # Try alternative approach - search and then explicitly click the result
            logger.warning(f"Role '{new_role}' may not have been populated, trying alternative selection")
            nova.act(f"In the role dropdown, find and click on the '{new_role}' option from the search results to select and populate it")
            time.sleep(1)
            
            # Verify again
            role_populated_retry = nova.act(
                f"Check if the role dropdown now shows '{new_role}' as the selected value",
                schema=BOOL_SCHEMA
            )
            
            if not (role_populated_retry.matches_schema and role_populated_retry.parsed_response):
                logger.error(f"Role '{new_role}' could not be selected and populated")
                print(f"❌ Role '{new_role}' could not be selected and populated")
                return False
        
        # Step 6: Verify the role was set correctly
        logger.debug("Verifying role field update")
        role_ok = nova.act(
            f"Check if the Role field now displays '{new_role}' as the selected value (not just in the dropdown search). Look for the role name showing as the current selection in the Role field.",
            schema=BOOL_SCHEMA
        )
        
        if role_ok.matches_schema and role_ok.parsed_response:
            logger.info(f"Role successfully updated to: {new_role}")
            print(f"✅ Role updated to: {new_role}")
            self.session_data['last_role_change_performed'] = True
            return True
        else:
            logger.error(f"Failed to set role to: {new_role} (verification failed)")
            print(f"❌ Failed to set role to: {new_role} (verification failed)")
            self.session_data['last_role_change_performed'] = False
            return False
    
    def change_user_branch_hierarchical(self, nova: NovaAct, branch_hierarchy: List[str], auto_save: bool = True) -> bool:
        """Change user branch using hierarchical navigation through branch_hierarchy.
        
        This method performs TWO major steps within the Roles tab:
        1. Change Bank user using hierarchical navigation (save & close)
        2. Change Scope using hierarchical navigation (save & close)
        
        Args:
            nova: NovaAct instance
            branch_hierarchy: List of hierarchical levels to navigate (e.g., ["VIB Bank", "North", "003"])
            auto_save: Whether to automatically save changes after each step
            
        Returns:
            bool: True if both bank user and scope were successfully changed, False otherwise
        """
        if not branch_hierarchy or len(branch_hierarchy) == 0:
            print("❌ Empty branch hierarchy provided")
            return False
            
        final_branch = branch_hierarchy[-1]  # Last element is the target branch
        print(f"🏢 Changing user branch using hierarchical path (2-step process): {' → '.join(branch_hierarchy)}")
        
        # Always ensure Roles tab active first (explicit, idempotent)
        nova.act("Click (or re-click) the 'Roles' tab in the Edit user modal to ensure it is active before starting the 2-step branch change process")
        
        # =================================================================
        # STEP 1: Change Bank User using hierarchical navigation
        # =================================================================
        print("🏦 STEP 1: Changing Bank User using hierarchical navigation...")
        
        # Initialize step tracking variables
        bank_user_needs_update = False
        scope_needs_update = False
        
        # Check if bank user already contains target branch
        bank_user_pre_check = nova.act(
            f"IMPORTANT: Look ONLY at the Bank user field (NOT the Scope field or any other field). Read the exact text content of the Bank user textbox. Return True ONLY if the Bank user field's text content contains '{final_branch}' as a substring. If the Bank user field does not contain '{final_branch}', return False. Ignore all other fields like Scope, Role, etc.", 
            schema=BOOL_SCHEMA
        )
        
        if not (bank_user_pre_check.matches_schema and bank_user_pre_check.parsed_response):
            bank_user_needs_update = True
            # Step 1a: Open bank user selector panel
            print("🔍 Opening bank user selection panel...")
            nova.act("In the Roles tab, click the button with three dots (...) next to the Bank user field to open the bank user selection panel")
            time.sleep(2)
            
            # Wait for bank user selection panel to load completely
            if not self.wait_for_loading_complete(nova, timeout_seconds=60, action_description="bank user selection panel to load"):
                print("❌ Timeout waiting for bank user selection panel to load")
                return False
            
            # Step 1b: Navigate through hierarchy levels for bank user
            for i, level in enumerate(branch_hierarchy):
                print(f"📍 Bank user navigation - level {i+1}/{len(branch_hierarchy)}: '{level}'")
                
                if i == 0:
                    # First level: Find and click on the bank level (VIB Bank)
                    print(f"🏦 Selecting bank level: '{level}'")
                    nova.act(f"In the leftmost column of the bank user selection panel, find and click on the item labeled '{level}' to expand it")
                elif i == 1:
                    # Second level: Find and click on the region level (North/South)
                    print(f"🌍 Selecting region level: '{level}'")
                    nova.act(f"In the middle column that appeared after selecting the bank, find and click on the item labeled '{level}' to expand it")
                else:
                    # Final level: Find and select the specific branch/bank user
                    print(f"🎯 Selecting final bank user: '{level}'")
                    # Use the search box in the rightmost column to find the specific bank user
                    nova.act(f"In the rightmost column, use the search input field (with placeholder 'Search ...') and type '{level}' to filter the bank users")
                    # Find and check the checkbox for the specific bank user
                    nova.act(f"In the filtered results in the rightmost column, find the row that contains '{level}' and click its checkbox to select it")
            
            # Step 1c: Apply bank user selection
            print("💾 Applying bank user selection...")
            nova.act("Click the purple 'Select' button at the bottom of the bank user selection panel to apply the selection")
            time.sleep(2)
            
            # Verify bank user selection was applied (hierarchy panel closes, stays in Edit user modal)
            bank_user_updated = nova.act(
                f"Verify that the Bank user field now contains '{final_branch}' and the hierarchy selection panel has closed. You should still be in the Edit user modal on the Roles tab.",
                schema=BOOL_SCHEMA
            )
            
            if bank_user_updated.matches_schema and bank_user_updated.parsed_response:
                print(f"✅ Bank user updated to: {final_branch}")
            else:
                print(f"❌ Failed to update bank user to: {final_branch}")
                return False
        else:
            print(f"ℹ️ Bank user already contains target token '{final_branch}'; skipping bank user update")
        
        # =================================================================
        # STEP 2: Change Scope using hierarchical navigation (ALWAYS EXECUTED)
        # =================================================================
        print("🎯 STEP 2: Changing Scope using hierarchical navigation...")
        print("ℹ️ Still in the same Edit user modal, now working on the Scope field...")
        
        # Check if scope already contains target branch
        scope_pre_check = nova.act(
            f"IMPORTANT: Look ONLY at the Scope field (NOT the Bank user field or any other field). Read the exact text content of the Scope textbox. Return True ONLY if the Scope field's text content contains '{final_branch}' as a substring. If the Scope field does not contain '{final_branch}', return False. Ignore all other fields like Bank user, Role, etc.", 
            schema=BOOL_SCHEMA
        )
        
        if not (scope_pre_check.matches_schema and scope_pre_check.parsed_response):
            scope_needs_update = True
            # Step 2a: Open scope selector panel
            print("🔍 Opening scope selection panel...")
            nova.act("In the same Edit user modal, click the FIRST non-empty scope input field to open the scope selection panel")
            time.sleep(2)
            
            # Wait for scope selection panel to load completely
            if not self.wait_for_loading_complete(nova, timeout_seconds=60, action_description="scope selection panel to load"):
                print("❌ Timeout waiting for scope selection panel to load")
                return False
            
            # Step 2b: Navigate through hierarchy levels for scope
            for i, level in enumerate(branch_hierarchy):
                print(f"📍 Scope navigation - level {i+1}/{len(branch_hierarchy)}: '{level}'")
                
                if i == 0:
                    # First level: Find and click on the bank level (VIB Bank)
                    print(f"🏦 Selecting bank level: '{level}'")
                    nova.act(f"In the leftmost column of the scope selection panel, find and click on the item labeled '{level}' to expand it")
                elif i == 1:
                    # Second level: Find and click on the region level (North/South)
                    print(f"🌍 Selecting region level: '{level}'")
                    nova.act(f"In the middle column that appeared after selecting the bank, find and click on the item labeled '{level}' to expand it")
                else:
                    # Final level: Find and select the specific branch
                    print(f"🎯 Selecting final scope branch: '{level}'")
                    # Use the search box in the rightmost column to find the specific branch
                    nova.act(f"In the rightmost column, use the search input field (with placeholder 'Search ...') and type '{level}' to filter the branches")
                    # Find and check the checkbox for the specific branch
                    nova.act(f"In the filtered results in the rightmost column, find the row that contains '{level}' and click its checkbox to select it")
            
            # Step 2c: Apply scope selection
            print("💾 Applying scope selection...")
            nova.act("Click the purple 'Select' button at the bottom of the scope selection panel to apply the branch selection")
            time.sleep(2)
            
            # Verify scope was updated
            scope_verify = nova.act(
                f"VERIFICATION: After the scope selection, look specifically at the Scope textbox only. Read its exact text content. Return True ONLY if the Scope field now contains '{final_branch}' as a substring. Return False if the Scope field does not contain '{final_branch}'. Ignore other fields like Bank user.",
                schema=BOOL_SCHEMA
            )
            
            if not (scope_verify.matches_schema and scope_verify.parsed_response):
                print(f"❌ Failed to update scope to: {final_branch}")
                return False
            else:
                print(f"✅ Scope updated to contain: {final_branch}")
        else:
            print(f"ℹ️ Scope already contains target token '{final_branch}'; skipping scope update")
        
        # =================================================================
        # FINAL VERIFICATION: Both Bank User and Scope must contain target
        # =================================================================
        print("🔍 Final verification: Checking both Bank User and Scope contain target branch...")
        
        # Double-check both fields contain the target branch
        final_bank_check = nova.act(
            f"VERIFICATION: Look specifically at the Bank user field only. Read its exact text content. Return True ONLY if the Bank user field contains '{final_branch}' as a substring. Return False if it does not contain '{final_branch}'. Do not consider any other fields.",
            schema=BOOL_SCHEMA
        )
        
        final_scope_check = nova.act(
            f"VERIFICATION: Look specifically at the Scope field only. Read its exact text content. Return True ONLY if the Scope field contains '{final_branch}' as a substring. Return False if it does not contain '{final_branch}'. Do not consider any other fields.",
            schema=BOOL_SCHEMA
        )
        
        # Both fields must contain the target branch
        both_fields_valid = (
            final_bank_check.matches_schema and final_bank_check.parsed_response and
            final_scope_check.matches_schema and final_scope_check.parsed_response
        )
        
        if not both_fields_valid:
            print(f"❌ Verification failed: Bank User or Scope does not contain '{final_branch}'")
            print(f"   Bank User contains target: {final_bank_check.parsed_response if final_bank_check.matches_schema else 'Error'}")
            print(f"   Scope contains target: {final_scope_check.parsed_response if final_scope_check.matches_schema else 'Error'}")
            return False
        
        # =================================================================
        # SAVE CHANGES (if auto_save enabled and updates were made)
        # =================================================================
        if auto_save:
            if bank_user_needs_update or scope_needs_update:
                print("💾 Saving changes...")
                save_result = nova.act("Click the green Save button to save all changes", schema=BOOL_SCHEMA)
                
                if save_result.matches_schema and save_result.parsed_response:
                    # Wait for save operation to complete
                    if self.wait_for_loading_complete(nova, timeout_seconds=60, action_description="save operation to complete"):
                        print(f"✅ All changes saved successfully for branch: {final_branch}")
                        self.session_data['last_branch_change_performed'] = True
                        self.session_data['branch_saved'] = True
                    else:
                        print(f"❌ Timeout during save operation for branch: {final_branch}")
                        return False
                else:
                    print(f"❌ Failed to save changes for branch: {final_branch}")
                    return False
            else:
                print("ℹ️ No changes needed - both fields already contain target branch")
                self.session_data['last_branch_change_performed'] = False
                self.session_data['branch_saved'] = True
        else:
            print(f"✅ Both bank user and scope verified to contain '{final_branch}' (save pending)")
            self.session_data['last_branch_change_performed'] = bank_user_needs_update or scope_needs_update
            self.session_data['branch_saved'] = False
        
        print(f"✅ SUCCESS: Both Bank User and Scope contain target branch '{final_branch}'")
        return True

    def _convert_to_hierarchy(self, branch_name: str) -> List[str]:
        """Convert a simple branch name to a default hierarchy format.
        
        This is a fallback for when new_branch is provided instead of branch_hierarchy.
        In practice, users should provide branch_hierarchy for proper hierarchical navigation.
        
        Args:
            branch_name: Simple branch name (e.g., "003_CAU GIAY")
            
        Returns:
            List[str]: Default hierarchy with the branch as the final level
        """
        # Default hierarchy structure - adjust based on your organization
        # This assumes a basic 3-level structure: Bank -> Region -> Branch
        return ["VIB Bank", "North", branch_name]  # Default to North region
    
    def save_changes(self, nova: NovaAct) -> bool:
        """Save the role and branch changes using the green save button"""
        print("💾 Saving changes...")
        
        # Click the green Save button (in the modal)
        nova.act("Find and click the green 'Save' button to save the changes")
        time.sleep(2)
        
        # Verify the save was successful
        save_success = nova.act("Check if the save was successful - look for success message or modal closes", 
                               schema=BOOL_SCHEMA)
        
        if save_success.matches_schema and save_success.parsed_response:
            print("✅ Changes saved successfully")
            return True
        else:
            # Check for error messages
            error_check = nova.act("Check if there are any error messages displayed indicating the save failed", 
                                 schema=BOOL_SCHEMA)
            if error_check.matches_schema and error_check.parsed_response:
                print("❌ Save failed - error message detected")
            else:
                print("⚠️ Save status unclear")
            return False
    
    def verify_changes(self, nova: NovaAct, user_id: str, expected_role: str, expected_branch: str) -> bool:
        """Verify that the role and branch changes were applied correctly"""
        print(f"🔍 Verifying changes for user {user_id}...")
        
        # Re-search for the user to refresh the data
        if not self.search_user(nova, user_id):
            print(f"❌ Could not find user {user_id} for verification")
            return False
        
        # Click edit again to view current values
        if not self.access_edit_form(nova):
            print("❌ Could not access edit form for verification")
            return False
        
        # Extract current role value
        current_role = nova.act("Extract the currently selected value from the Role dropdown in the edit form")
        print(f"Current role: {current_role.response}")
        
        # Extract current branch/scope value
        current_branch = nova.act("Extract the currently selected value from the Scope dropdown in the edit form")
        print(f"Current branch/scope: {current_branch.response}")
        
        # Check if the values match what was expected
        role_matches = expected_role.lower() in current_role.response.lower()
        branch_matches = expected_branch.lower() in current_branch.response.lower()
        
        if role_matches and branch_matches:
            print("✅ Changes verified successfully - both role and branch match expected values")
            # Close the edit form
            nova.act("Close the edit form by clicking cancel or the X button")
            return True
        else:
            print(f"❌ Verification failed:")
            if not role_matches:
                print(f"   Role mismatch: expected '{expected_role}', found '{current_role.response}'")
            if not branch_matches:
                print(f"   Branch mismatch: expected '{expected_branch}', found '{current_branch.response}'")
            # Close the edit form
            nova.act("Close the edit form by clicking cancel or the X button")
            return False
    
    def process_single_user(self, nova: NovaAct, user_request: UserChangeRequest) -> bool:
        """Process role and branch change for a single user ensuring at most one final save.

        Logic:
        - If both role & branch requested: change role, change branch (no auto save), then one save.
        - If only branch: branch auto_save True (internal save) unless no change.
        - If only role: change role then save if changed.
        - If branch_hierarchy is provided, use hierarchical navigation instead of simple branch change.
        """
        logger.info(f"Starting processing for user: {user_request.target_user}")
        print(f"\n👤 Processing user: {user_request.target_user}")
        
        try:
            logger.debug(f"Searching for user: {user_request.target_user}")
            if not self.search_user(nova, user_request.target_user):
                logger.error(f"User not found: {user_request.target_user}")
                self.results.append(RoleChangeResult(
                    user_email=user_request.target_user,
                    new_role=user_request.new_role or "unchanged",
                    new_branch=user_request.new_branch or "unchanged",
                    status="failed - user not found",
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                ))
                return False
            
            # Track what changes are requested
            role_requested = bool(user_request.new_role)
            branch_requested = bool(user_request.new_branch) or bool(user_request.branch_hierarchy)
            use_hierarchy = bool(user_request.branch_hierarchy)
            
            logger.debug(f"Change requests - Role: {role_requested}, Branch: {branch_requested}, Hierarchy: {use_hierarchy}")

            # Both role and branch (single save)
            if role_requested and branch_requested:
                logger.info("Processing both role and branch changes")
                
                logger.debug(f"Changing role to: {user_request.new_role}")
                if not self.change_user_role(nova, user_request.new_role):
                    logger.error("Role change failed")
                    self.results.append(RoleChangeResult(
                        user_email=user_request.target_user,
                        new_role=user_request.new_role,
                        new_branch=user_request.new_branch or "unchanged",
                        status="failed - role change failed",
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    return False
                
                role_changed = self.session_data.get('last_role_change_performed', False)
                logger.debug(f"Role change performed: {role_changed}")
                
                # Determine branch hierarchy to use
                if use_hierarchy:
                    branch_hierarchy = user_request.branch_hierarchy
                    logger.debug("Using provided hierarchical branch change")
                else:
                    branch_hierarchy = self._convert_to_hierarchy(user_request.new_branch)
                    logger.debug(f"Using converted hierarchy for branch: {user_request.new_branch}")
                
                # Use hierarchical branch change (includes both bank user and scope)
                branch_success = self.change_user_branch_hierarchical(nova, branch_hierarchy, auto_save=False)
                
                if not branch_success:
                    logger.error("Branch change failed")
                    self.results.append(RoleChangeResult(
                        user_email=user_request.target_user,
                        new_role=user_request.new_role or "unchanged",
                        new_branch=user_request.new_branch or "unchanged",
                        status="failed - branch change failed",
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    return False
                
                branch_changed = self.session_data.get('last_branch_change_performed', False)
                logger.debug(f"Changes - Branch: {branch_changed}")
                
                # Only save if there were actual changes
                if role_changed or branch_changed:
                    logger.debug("Saving changes")
                    if not self.save_changes(nova):
                        logger.error("Save failed")
                        self.results.append(RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status="failed - save failed",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        return False
                else:
                    logger.info("No changes needed - all fields already set correctly")
                    print("ℹ️ No changes needed - all fields already set correctly")
                    # Close the edit modal since no changes were made
                    nova.act("Close the edit modal by clicking Cancel, X button, or clicking outside the modal")
                        
            elif role_requested:
                logger.info("Processing role change only")
                if not self.change_user_role(nova, user_request.new_role):
                    logger.error("Role change failed")
                    self.results.append(RoleChangeResult(
                        user_email=user_request.target_user,
                        new_role=user_request.new_role,
                        new_branch=user_request.new_branch or "unchanged",
                        status="failed - role change failed",
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    return False
                
                # Only save if there was an actual role change
                if self.session_data.get('last_role_change_performed'):
                    logger.debug("Saving role changes")
                    if not self.save_changes(nova):
                        logger.error("Save failed after role change")
                        self.results.append(RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status="failed - save failed",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        return False
                else:
                    logger.info("No changes needed - role already set correctly")
                    print("ℹ️ No changes needed - role already set correctly")
                        
            elif branch_requested:
                logger.info("Processing branch change only")
                
                # Determine branch hierarchy to use
                if use_hierarchy:
                    branch_hierarchy = user_request.branch_hierarchy
                    logger.debug("Using provided hierarchical branch change with auto-save")
                else:
                    branch_hierarchy = self._convert_to_hierarchy(user_request.new_branch)
                    logger.debug(f"Using converted hierarchy for branch: {user_request.new_branch}")
                
                # Use hierarchical branch change with auto_save=True (includes both bank user and scope)
                branch_success = self.change_user_branch_hierarchical(nova, branch_hierarchy, auto_save=True)
                
                if not branch_success:
                    logger.error("Branch change failed")
                    self.results.append(RoleChangeResult(
                        user_email=user_request.target_user,
                        new_role=user_request.new_role or "unchanged",
                        new_branch=user_request.new_branch or "unchanged",
                        status="failed - branch change failed",
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    return False
                
                # Check if changes were actually performed
                branch_changed = self.session_data.get('last_branch_change_performed', False)
                logger.debug(f"Branch change performed: {branch_changed}")
                
                if not branch_changed:
                    logger.info("No changes needed - branch already set correctly")
                    print("ℹ️ No changes needed - branch already set correctly")
            else:
                logger.info("No changes requested (neither role nor branch)")
                print("ℹ️ No changes requested (neither role nor branch)")

            # Determine the effective new branch for logging
            effective_new_branch = user_request.new_branch or "unchanged"
            if user_request.branch_hierarchy:
                effective_new_branch = user_request.branch_hierarchy[-1]  # Use final level from hierarchy

            # Determine if any changes were actually made
            role_changed = self.session_data.get('last_role_change_performed', False)
            branch_changed = self.session_data.get('last_branch_change_performed', False)
            
            # Create appropriate status message
            if role_requested and branch_requested:
                changed_items = []
                if role_changed: changed_items.append("role")
                if branch_changed: changed_items.append("branch")
                
                if changed_items:
                    status = f"success - {' and '.join(changed_items)} updated"
                else:
                    status = "success - no changes needed, already configured correctly"
            elif role_requested:
                if role_changed:
                    status = "success - role updated"
                else:
                    status = "success - role already correct"
            elif branch_requested:
                if branch_changed:
                    status = "success - branch updated"
                else:
                    status = "success - branch already correct"
            else:
                status = "success - no changes requested"

            logger.info(f"User processing completed with status: {status}")
            self.results.append(RoleChangeResult(
                user_email=user_request.target_user,
                new_role=user_request.new_role or "unchanged",
                new_branch=effective_new_branch,
                status=status,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            ))
            print(f"✅ Successfully processed {user_request.target_user}: {status}")
            return True

        except Exception as e:
            logger.exception(f"Error processing user {user_request.target_user}: {e}")
            print(f"❌ Error processing {user_request.target_user}: {e}")
            self.results.append(RoleChangeResult(
                user_email=user_request.target_user,
                new_role=user_request.new_role or "unchanged",
                new_branch=user_request.new_branch or "unchanged",
                status=f"failed - {str(e)}",
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            ))
            return False
    
    def run_batch(self, input_file: str, password: str = None, per_user_session: bool = True, parallel_workers: int | None = None, start_retries: int = 2) -> bool:
        """Run the complete role and branch change process for multiple users.

        If per_user_session is True, launches a fresh browser session per user to isolate state.
        Returns True only if all user operations succeed.
        
        Note: parallel_workers is deprecated and ignored. App now runs in single worker mode for stability.
        """
        logger.info(f"Starting batch processing from file: {input_file}")
        
        # Force single worker mode for stability
        parallel_workers = None
        logger.info("App configured for single worker mode (parallel workers disabled)")
        logger.debug(f"Parameters - per_user_session: {per_user_session}, parallel_workers: {parallel_workers}, start_retries: {start_retries}")
        
        # Load configuration
        try:
            config = self.load_input_config(input_file)
            logger.info(f"Loaded configuration for {len(config.users)} users")
        except Exception as e:
            logger.error(f"Configuration error: {e}")
            print(f"❌ Configuration error: {e}")
            return False

        # Determine password precedence: config > passed param > prompt
        admin_password = config.admin_credentials.password or password
        if not admin_password:
            admin_password = getpass.getpass(f"Enter password for {config.admin_credentials.username}: ")

        success_count = 0

        # Note: Parallel execution has been removed for stability
        if parallel_workers and parallel_workers > 1:
            logger.warning("Parallel workers parameter ignored - app now runs in single worker mode for stability")
            print("⚠️ Parallel workers parameter ignored - app now runs in single worker mode for stability")

        # Single worker mode execution
        if per_user_session:
            logger.info("Using isolated browser session per user (single worker mode)")
            print("🔁 Using isolated browser session per user (single worker mode)")
            for user_request in config.users:
                session_started = False
                for attempt in range(1, start_retries + 1):
                    try:
                        logger.debug(f"Starting session attempt {attempt} for user: {user_request.target_user}")
                        with self.create_nova_act_instance(config.admin_credentials.csp_admin_url) as nova:
                            session_started = True
                            logger.debug("Nova Act session started successfully")
                            
                            if not self.login(nova, config.admin_credentials.username, admin_password):
                                logger.error("Login failed")
                                self.results.append(RoleChangeResult(
                                    user_email=user_request.target_user,
                                    new_role=user_request.new_role or "unchanged",
                                    new_branch=user_request.new_branch or "unchanged",
                                    status="failed - login failed",
                                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                                ))
                                break
                            
                            if not self.navigate_to_user_management(nova):
                                logger.error("Navigation to user management failed")
                                self.results.append(RoleChangeResult(
                                    user_email=user_request.target_user,
                                    new_role=user_request.new_role or "unchanged",
                                    new_branch=user_request.new_branch or "unchanged",
                                    status="failed - navigation failed",
                                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                                ))
                                break
                            
                            if self.process_single_user(nova, user_request):
                                success_count += 1
                                logger.info(f"Successfully processed user: {user_request.target_user}")
                            break
                    except StartFailed as sf:
                        logger.warning(f"StartFailed (attempt {attempt}/{start_retries}) for {user_request.target_user}: {sf}")
                        print(f"⚠️ StartFailed (attempt {attempt}/{start_retries}) for {user_request.target_user}: {sf}")
                        if attempt < start_retries:
                            time.sleep(2 * attempt)
                            continue
                        logger.error(f"StartFailed - all retries exhausted for {user_request.target_user}")
                        self.results.append(RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status="failed - start timeout",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                    except Exception as e:
                        logger.exception(f"Session error for {user_request.target_user}: {e}")
                        print(f"❌ Session error for {user_request.target_user}: {e}")
                        self.results.append(RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status=f"failed - {str(e)}",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        break
                time.sleep(1)  # polite gap between sessions
        else:
            logger.info("Using single browser session for all users")
            with self.create_nova_act_instance(config.admin_credentials.csp_admin_url) as nova:
                try:
                    if not self.login(nova, config.admin_credentials.username, admin_password):
                        logger.error("Initial login failed")
                        self.save_results()
                        return False
                    if not self.navigate_to_user_management(nova):
                        logger.error("Initial navigation failed")
                        self.save_results()
                        return False
                    for user_request in config.users:
                        if self.process_single_user(nova, user_request):
                            success_count += 1
                            logger.info(f"Successfully processed user: {user_request.target_user}")
                        time.sleep(1)
                except Exception as e:
                    logger.exception(f"Batch processing error: {e}")
                    print(f"❌ Batch processing error: {e}")

        total_users = len(config.users)
        logger.info(f"Batch processing completed. Success rate: {(success_count/total_users)*100:.1f}%")
        print(f"\n📊 Batch Processing Summary:")
        print(f"   Total users: {total_users}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {total_users - success_count}")
        if total_users:
            print(f"   Success rate: {(success_count/total_users)*100:.1f}%")

        self.save_results()
        return success_count == total_users


def create_sample_input_file(filename: str = "sample_input.json"):
    """Create a sample input file for reference"""
    sample_data = {
        "admin_credentials": {
            "username": "admin_user",
            "password": "admin_password",
            "csp_admin_url": "https://your-csp-admin-portal.com"
        },
        "users": [
            {
                "target_user": "user1@example.com",
                "new_role": "manager",
                "branch_hierarchy": ["VIB Bank", "North", "001_HA NOI"]
            },
            {
                "target_user": "user2@example.com",
                "new_role": "employee", 
                "branch_hierarchy": ["VIB Bank", "South", "002_HO CHI MINH"]
            },
            {
                "target_user": "user3@example.com",
                "new_role": "supervisor",
                "branch_hierarchy": ["VIB Bank", "North", "003_CAU GIAY"]
            },
            {
                "target_user": "user4@example.com",
                "new_role": "employee",
                "new_branch": "005_THANH XUAN"  # Will be converted to default hierarchy
            }
        ]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Sample input file created: {filename}")
    print("💡 Recommended: Use 'branch_hierarchy' for proper hierarchical navigation")
    print("💡 Note: 'new_branch' is supported for backward compatibility but will use default hierarchy")


def main(
    input_file: str,
    password: str = None,
    per_user_session: bool = True,
    start_retries: int = 2,
    nova_act_api_key: str = None,
    logs_directory: str = None
):
    """
    Execute CSP admin role and branch change automation from JSON input file.
    
    Args:
        input_file: Path to JSON file containing user change requests
        password: Admin password (will prompt if not provided)
        per_user_session: Launch a new browser session per user for isolation (default True)
        start_retries: Number of retries for starting browser sessions (default 2)
        nova_act_api_key: Nova Act API key (if not provided, will use environment variable)
        logs_directory: Directory to save Nova Act traces and logs
    
    Note: App now runs in single worker mode for improved stability and reliability.
    """
    
    logger.info("CSP Admin Role and Branch Change Automation starting")
    
    if not input_file:
        logger.error("No input file provided")
        print("Error: Please provide an input file")
        print("Usage: python -m nova_act.samples.vib_csp_automation.csp_admin_change_role_and_branch --input_file input.json")
        return
    
    if not Path(input_file).exists():
        logger.error(f"Input file not found: {input_file}")
        print(f"Error: Input file not found: {input_file}")
        print("You can create a sample input file using the create_sample_input_file() function")
        return
    
    # Get Nova Act API key from parameter or configuration
    if not nova_act_api_key:
        try:
            nova_act_api_key = get_nova_act_api_key()
            logger.info("Using Nova Act API key from configuration")
            print("✅ Using Nova Act API key from configuration")
        except Exception as e:
            logger.error(f"Error getting Nova Act API key: {e}")
            print(f"❌ Error getting Nova Act API key: {e}")
            return
    
    print(f"🚀 Starting CSP Admin Role and Branch Change Automation")
    print(f"� Input file: {input_file}")
    print("=" * 50)
    
    # Create and run the automation
    changer = CSPAdminRoleAndBranchChanger("", nova_act_api_key, logs_directory)  # URL will be loaded from config
    success = changer.run_batch(input_file, password, per_user_session=per_user_session, start_retries=start_retries)
    
    if success:
        logger.info("All users processed successfully")
        print("\n✅ All users processed successfully!")
    else:
        logger.warning("Some users failed to process")
        print("\n⚠️ Some users failed to process. Check results file for details.")


if __name__ == "__main__":
    import fire
    fire.Fire(main)
