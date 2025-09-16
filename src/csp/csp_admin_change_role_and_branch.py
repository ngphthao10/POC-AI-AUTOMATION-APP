"""
CSP Admin Change Role and Branch Automation

This automation handles the process of changing user roles and branch assignments 
in CSP web applications for IT support teams. It supports both simple branch changes
and hierarchical branch navigation.

Usage:
python -m src.csp.csp_admin_change_role_and_branch --input_file src/csp/input.json [--per_user_session False] [--parallel_workers 4]

Note: per_user_session defaults to True (isolation ON). Pass --per_user_session False to reuse a single browser session.

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
            "new_branch": "branch_001"
        },
        {
            "target_user": "user2@example.com", 
            "new_role": "employee",
            "new_branch": "branch_002",
            "branch_hierarchy": ["VIB Bank", "North", "002_HA NOI"]
        }
    ]
}

Branch Hierarchy Support:
- If 'branch_hierarchy' is provided, the automation will navigate through the hierarchical path step by step
- Each element in the array represents a level in the hierarchy (e.g., Bank → Region → Branch)
- The final element in the hierarchy is considered the target branch
- If 'branch_hierarchy' is provided, 'new_branch' can be omitted or will be ignored
- This supports complex organizational structures where branches are nested under regions or departments
"""

import getpass
import time
import json
import fire
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from pathlib import Path
from typing import Optional, List, Dict
from pydantic import BaseModel

from nova_act import NovaAct, BOOL_SCHEMA
from nova_act.types.errors import StartFailed

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
    
    def __init__(self, csp_admin_url: str, nova_act_api_key: str = None):
        self.csp_admin_url = csp_admin_url
        self.nova_act_api_key = nova_act_api_key
        self.session_data = {}
        self.results: List[RoleChangeResult] = []
    
    def load_input_config(self, input_file: str) -> InputConfig:
        """Load and validate input configuration from JSON file"""
        try:
            input_path = Path(input_file)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = InputConfig.model_validate(data)
            print(f"✅ Loaded configuration for {len(config.users)} users")
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {input_file}: {e}")
        except Exception as e:
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
        """Handle admin login process"""
        print(f"🔐 Logging into VIB Portal as: {username}")
        
        # Enter username with Unicode encoding for special characters
        nova.act("Find and click the username field")
        # unicode_username = username.encode('unicode_escape').decode('ascii')
        username_field = nova.page.locator('input').first
        username_field.clear()
        username_field.type(username)
        
        # Enter password
        nova.act("Find and click the password field")
        nova.page.keyboard.type(password)
        
        # Submit login
        nova.act("Click the purple Enter button to login")
        time.sleep(3)
        
        # Check for successful login by verifying admin interface is displayed
        admin_interface_displayed = nova.act(
            "Check if the CSP admin interface is successfully displayed - look for the left navigation menu with Administration section, user management table, any admin dashboard elements, or customer service portal page", 
            schema=BOOL_SCHEMA
        )
        
        if admin_interface_displayed.matches_schema and admin_interface_displayed.parsed_response:
            print("✅ Login successful - admin interface displayed!")
            return True
        else:
            print("❌ Login failed - admin interface not displayed")
            return False
    
    def navigate_to_user_management(self, nova: NovaAct) -> bool:
        """Navigate to user management section"""
        print("🧭 Navigating to user management...")
        
        # Check if already on users page
        already_on_users = nova.act("Check if we can see a user management table with columns like ID, Login, Name, Scope", 
                                   schema=BOOL_SCHEMA)
        
        if already_on_users.matches_schema and already_on_users.parsed_response:
            print("✅ Already on user management page")
            return True
        
        # Navigate: Administration → Users
        nova.act("Click on Administration in the left navigation")
        nova.act("Click on Users under Administration")
        time.sleep(2)
        
        # Verify we reached the users page
        success = nova.act("Check if we can see the user management interface with search fields and user table", 
                          schema=BOOL_SCHEMA)
        
        if success.matches_schema and success.parsed_response:
            print("✅ Successfully navigated to user management")
            return True
        else:
            print("❌ Failed to navigate to user management")
            return False
    
    def search_user(self, nova: NovaAct, target_user: str) -> bool:
        """Search for target user and open edit form"""
        print(f"🔍 Searching for user: {target_user}")
        
        # Expand filters if needed and search
        nova.act("Click More filters next to the search fields. Stay there. Don't return")
        nova.act(f"Enter '{target_user}' in the Login field")
        nova.act("Click the purple Search button")
        time.sleep(3)
        
        # Check for results
        no_records = nova.act("Check if 'no records found' or empty table", schema=BOOL_SCHEMA)
        if no_records.matches_schema and no_records.parsed_response:
            print(f"❌ No records found for user: {target_user}")
            return False
        # Ensure the specific user row is present before interacting
        row_present = nova.act(
            f"Check that a table row exists where the Login cell text contains '{target_user}' (case-insensitive, substring match acceptable)",
            schema=BOOL_SCHEMA
        )
        if not (row_present.matches_schema and row_present.parsed_response):
            print(f"❌ Could not uniquely identify row for user: {target_user}")
            return False

        # Attempt to open edit modal robustly (retry once)
        for attempt in range(1, 3):
            if attempt > 1:
                print("↻ Retrying opening Edit modal")
            # Open actions dropdown for the row containing the target user
            nova.act(
                f"Within the table row whose Login cell contains '{target_user}' (substring match), click its Actions dropdown button (labeled 'Select')"
            )
            # Click only the 'Edit' option (avoid View details / Manage authentication)
            nova.act(
                "In the opened dropdown menu, click the menu item whose visible text is exactly 'Edit' (do not click other items)"
            )
            time.sleep(1)
            edit_loaded = nova.act(
                "Check if edit modal displayed (look for modal header or form fields indicating editing user)",
                schema=BOOL_SCHEMA
            )
            if edit_loaded.matches_schema and edit_loaded.parsed_response:
                print(f"✅ Edit form loaded for user {target_user}")
                return True
        print(f"❌ Failed to load edit form for {target_user} after retries")
        return False
    
    def change_user_role(self, nova: NovaAct, new_role: str) -> bool:
        """Change user role using the Roles tab in the Edit user modal"""
        print(f"👤 Changing user role to: {new_role}")
        # Ensure we're on the Roles tab before any checks
        nova.act("Click on the 'Roles' tab in the Edit user modal (ensure Role field visible)")
        # Capture whether role already matches before overwrite
        pre_match = nova.act(
            f"Check if the visible Role input currently shows '{new_role}' exactly (True if matches, False otherwise)",
            schema=BOOL_SCHEMA
        )
        
        # If role already matches, return early without any processing
        if pre_match.matches_schema and pre_match.parsed_response:
            print(f"ℹ️ Role already set to '{new_role}' - no change needed")
            self.session_data['last_role_change_performed'] = False
            return True
        
        # Composite overwrite without selecting from dropdown suggestions
        nova.act(
            f"If multiple role input fields are present, identify ONLY the one that already displays a non-empty value (current role). Click that populated field once to focus it. Click the option contain '{new_role}' to select it. Do NOT click any second/duplicate/empty role field or placeholder. Without opening a dropdown or clicking any option, select all text in that focused populated field and replace it with '{new_role}'. Do NOT click any 'Select role' option or any list item. Do NOT click any 'Close' button."
        )

        # Verify field text now shows desired value
        role_ok = nova.act(
            f"Confirm the role input now exactly shows '{new_role}' (case-insensitive match acceptable). Return True if so.",
            schema=BOOL_SCHEMA
        )
        if role_ok.matches_schema and role_ok.parsed_response:
            print(f"✅ Role updated to: {new_role}")
            self.session_data['last_role_change_performed'] = True
            return True
        print(f"❌ Failed to set role to: {new_role} (post-verify mismatch)")
        self.session_data['last_role_change_performed'] = False
        return False
    
    def change_user_branch_hierarchical(self, nova: NovaAct, branch_hierarchy: List[str], auto_save: bool = True) -> bool:
        """Change user branch using hierarchical navigation through branch_hierarchy.
        
        Args:
            nova: NovaAct instance
            branch_hierarchy: List of hierarchical levels to navigate (e.g., ["VIB Bank", "North", "003"])
            auto_save: Whether to automatically save changes after selection
            
        Returns:
            bool: True if branch was successfully changed, False otherwise
        """
        if not branch_hierarchy or len(branch_hierarchy) == 0:
            print("❌ Empty branch hierarchy provided")
            return False
            
        final_branch = branch_hierarchy[-1]  # Last element is the target branch
        print(f"🏢 Changing user branch using hierarchical path: {' → '.join(branch_hierarchy)}")
        
        # Always ensure Roles tab active first (explicit, idempotent)
        nova.act("Click (or re-click) the 'Roles' tab in the Edit user modal to ensure it is active before inspecting scope inputs")
        
        # Composite pre-check without opening panel - check if final branch already present
        pre_token = nova.act(
            f"Just read the current Scope textbox (no clicks) and return True if it already CONTAINS '{final_branch}' (substring acceptable).", 
            schema=BOOL_SCHEMA
        )
        if pre_token.matches_schema and pre_token.parsed_response:
            print(f"ℹ️ Branch already contains target token '{final_branch}'; skipping")
            self.session_data['last_branch_change_performed'] = False
            return True
        
        # Step 1: Open scope selector panel
        print("🔍 Opening scope selection panel...")
        nova.act("Ensure 'Roles' tab is active, then click the FIRST non-empty scope input (not the empty placeholder) to open the scope selection panel")
        
        # Step 2: Navigate through hierarchy levels step by step
        for i, level in enumerate(branch_hierarchy):
            print(f"📍 Navigating to level {i+1}/{len(branch_hierarchy)}: '{level}'")
            
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
                print(f"🎯 Selecting final branch: '{level}'")
                # Use the search box in the rightmost column to find the specific branch
                nova.act(f"In the rightmost column, use the search input field (with placeholder 'Search ...') and type '{level}' to filter the branches")
                # Find and check the checkbox for the specific branch
                nova.act(f"In the filtered results in the rightmost column, find the row that contains '{level}' and click its checkbox to select it")
        
        # Step 3: Apply selection
        print("💾 Applying branch selection...")
        nova.act("Click the purple 'Select' button at the bottom of the scope selection panel to apply the branch selection")
        time.sleep(2)
        
        if auto_save:
            # Post-action verify + save combined
            verify_and_save = nova.act(
                f"Without reopening the selector, confirm the Scope textbox now CONTAINS '{final_branch}'. If yes, click the green Save button, wait for success indication (modal closes or success toast/message). Return True only if token present and success message or close observed.",
                schema=BOOL_SCHEMA
            )
            if verify_and_save.matches_schema and verify_and_save.parsed_response:
                print(f"✅ Hierarchical scope updated & saved for branch: {final_branch}")
                self.session_data['last_branch_change_performed'] = True
                self.session_data['branch_saved'] = True
                return True
            print(f"❌ Failed to update/save hierarchical branch: {final_branch}")
            self.session_data['last_branch_change_performed'] = False
            self.session_data['branch_saved'] = False
            return False
        else:
            # Verify only (no save)
            verify_only = nova.act(
                f"Without reopening the selector, confirm the Scope textbox now CONTAINS '{final_branch}'. Return True if token present (do NOT click Save).",
                schema=BOOL_SCHEMA
            )
            if verify_only.matches_schema and verify_only.parsed_response:
                print(f"✅ Hierarchical scope updated (pending save) for branch: {final_branch}")
                self.session_data['last_branch_change_performed'] = True
                self.session_data['branch_saved'] = False
                return True
            print(f"❌ Failed to update hierarchical branch (no save path): {final_branch}")
            self.session_data['last_branch_change_performed'] = False
            self.session_data['branch_saved'] = False
            return False

    def change_bank_user_hierarchical(self, nova: NovaAct, branch_hierarchy: List[str]) -> bool:
        """Change bank user in the Person tab using hierarchical navigation through branch_hierarchy.
        
        Args:
            nova: NovaAct instance
            branch_hierarchy: List of hierarchical levels to navigate (e.g., ["VIB Bank", "North", "003_CAU GIAY"])
            
        Returns:
            bool: True if bank user was successfully changed, False otherwise
        """
        if not branch_hierarchy or len(branch_hierarchy) == 0:
            print("❌ Empty branch hierarchy provided for bank user")
            return False
            
        final_branch = branch_hierarchy[-1]  # Last element is the target branch
        print(f"🏦 Changing bank user using hierarchical path: {' → '.join(branch_hierarchy)}")
        
        # Ensure we're on the Roles tab before any checks
        nova.act("Click on the 'Roles' tab in the Edit user modal")
        
        # Composite pre-check without opening panel - check if final branch already present in Bank user field
        pre_token = nova.act(
            f"Just read the current Bank user textbox (no clicks) and return True if it already CONTAINS '{final_branch}' (substring acceptable).", 
            schema=BOOL_SCHEMA
        )
        if pre_token.matches_schema and pre_token.parsed_response:
            print(f"ℹ️ Bank user already contains target token '{final_branch}'; skipping")
            self.session_data['last_bank_user_change_performed'] = False
            return True
        
        # Step 1: Open bank user selector panel
        print("🔍 Opening bank user selection panel...")
        nova.act("In the Person tab, click the button with three dots (...) next to the Bank user field to open the bank user selection panel")
        time.sleep(2)
        
        # Step 2: Navigate through hierarchy levels step by step
        for i, level in enumerate(branch_hierarchy):
            print(f"📍 Navigating to bank user level {i+1}/{len(branch_hierarchy)}: '{level}'")
            
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
                nova.act(f"In the rightmost column, use the search input field (with placeholder 'Search ...' if available) and type '{level}' to filter the bank users")
                # Find and check the checkbox for the specific bank user
                nova.act(f"In the filtered results in the rightmost column, find the row that contains '{level}' and click its checkbox to select it")
        
        # Step 3: Apply selection
        print("💾 Applying bank user selection...")
        nova.act("Click the purple 'Select' button at the bottom of the bank user selection panel to apply the selection")
        time.sleep(2)
        
        # Verify the change
        verify_change = nova.act(
            f"Without reopening the selector, confirm the Bank user textbox now CONTAINS '{final_branch}'. Return True if token present.",
            schema=BOOL_SCHEMA
        )
        
        if verify_change.matches_schema and verify_change.parsed_response:
            print(f"✅ Bank user updated using hierarchical path: {final_branch}")
            self.session_data['last_bank_user_change_performed'] = True
            return True
        else:
            print(f"❌ Failed to update bank user using hierarchical path: {final_branch}")
            self.session_data['last_bank_user_change_performed'] = False
            return False

    def change_user_branch(self, nova: NovaAct, new_branch: str, auto_save: bool = True) -> bool:
        """Change user branch using the Scope control.

        If auto_save is True (default), the method will verify and click Save inside the composite action.
        If auto_save is False, it will only perform the selection and verification (no Save click); caller must save later.
        """
        print(f"🏢 Changing user branch to: {new_branch}")
        # Always ensure Roles tab active first (explicit, idempotent)
        nova.act("Click (or re-click) the 'Roles' tab in the Edit user modal to ensure it is active before inspecting scope inputs")
        # Composite pre-check without opening panel
        pre_token = nova.act(
            f"Just read the current Scope textbox (no clicks) and return True if it already CONTAINS '{new_branch}' (substring acceptable).", schema=BOOL_SCHEMA
        )
        if pre_token.matches_schema and pre_token.parsed_response:
            print("ℹ️ Branch already contains target token; skipping")
            self.session_data['last_branch_change_performed'] = False
            return True
        # Single composite action: activate Roles tab, open correct scope input, open panel, search & select, apply
        composite = nova.act(
            f"Do ALL of these steps atomically: (1) Ensure 'Roles' tab is active (click if not); (2) Click the FIRST non-empty scope input (not the empty placeholder) to open the scope selection panel; (3) Once panel visible, click FIRST selectable item in leftmost column to focus; (4) Focus rightmost column search input with placeholder 'Search ...' and replace text with '{new_branch}'; (5) In filtered results find row whose label contains '{new_branch}' (case-insensitive, substring match acceptable) and ensure its checkbox is checked; (6) Click the purple Select button to apply. Avoid extra intermediate confirmations or reopening the panel.)"
        )
        if auto_save:
            # Post-action verify + save combined
            verify_and_save = nova.act(
                f"Without reopening the selector, confirm the Scope textbox now CONTAINS '{new_branch}'. If yes, click the green Save button, wait for success indication (modal closes or success toast/message). Return True only if token present and success message or close observed.",
                schema=BOOL_SCHEMA
            )
            if verify_and_save.matches_schema and verify_and_save.parsed_response:
                print(f"✅ Scope updated & saved for branch token: {new_branch}")
                self.session_data['last_branch_change_performed'] = True
                self.session_data['branch_saved'] = True
                return True
            print(f"❌ Failed to update/save branch token: {new_branch}")
            self.session_data['last_branch_change_performed'] = False
            self.session_data['branch_saved'] = False
            return False
        else:
            # Verify only (no save)
            verify_only = nova.act(
                f"Without reopening the selector, confirm the Scope textbox now CONTAINS '{new_branch}'. Return True if token present (do NOT click Save).",
                schema=BOOL_SCHEMA
            )
            if verify_only.matches_schema and verify_only.parsed_response:
                print(f"✅ Scope updated (pending save) for branch token: {new_branch}")
                self.session_data['last_branch_change_performed'] = True
                self.session_data['branch_saved'] = False
                return True
            print(f"❌ Failed to update branch token (no save path): {new_branch}")
            self.session_data['last_branch_change_performed'] = False
            self.session_data['branch_saved'] = False
            return False
    
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
        print(f"\n👤 Processing user: {user_request.target_user}")
        try:
            if not self.search_user(nova, user_request.target_user):
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

            # Both role and branch (single save)
            if role_requested and branch_requested:
                # Change bank user first (if using hierarchy)
                if use_hierarchy:
                    if not self.change_bank_user_hierarchical(nova, user_request.branch_hierarchy):
                        self.results.append(RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role,
                            new_branch=user_request.new_branch or "unchanged",
                            status="failed - bank user change failed",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        return False
                
                if not self.change_user_role(nova, user_request.new_role):
                    self.results.append(RoleChangeResult(
                        user_email=user_request.target_user,
                        new_role=user_request.new_role,
                        new_branch=user_request.new_branch or "unchanged",
                        status="failed - role change failed",
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    return False
                role_changed = self.session_data.get('last_role_change_performed', False)
                
                # Use hierarchical or simple branch change
                if use_hierarchy:
                    branch_success = self.change_user_branch_hierarchical(nova, user_request.branch_hierarchy, auto_save=False)
                else:
                    branch_success = self.change_user_branch(nova, user_request.new_branch, auto_save=False)
                
                if not branch_success:
                    self.results.append(RoleChangeResult(
                        user_email=user_request.target_user,
                        new_role=user_request.new_role or "unchanged",
                        new_branch=user_request.new_branch or "unchanged",
                        status="failed - branch change failed",
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    return False
                
                branch_changed = self.session_data.get('last_branch_change_performed', False)
                bank_user_changed = self.session_data.get('last_bank_user_change_performed', False)
                
                # Only save if there were actual changes
                if role_changed or branch_changed or bank_user_changed:
                    if not self.save_changes(nova):
                        self.results.append(RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status="failed - save failed",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        return False
                else:
                    print("ℹ️ No changes needed - all fields already set correctly")
                    # Close the edit modal since no changes were made
                    nova.act("Close the edit modal by clicking Cancel, X button, or clicking outside the modal")
                        
            elif role_requested:
                if not self.change_user_role(nova, user_request.new_role):
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
                    if not self.save_changes(nova):
                        self.results.append(RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status="failed - save failed",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        return False
                else:
                    print("ℹ️ No changes needed - role already set correctly")
                        
            elif branch_requested:
                # Change bank user first (if using hierarchy)
                if use_hierarchy:
                    if not self.change_bank_user_hierarchical(nova, user_request.branch_hierarchy):
                        self.results.append(RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status="failed - bank user change failed",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        return False
                
                # Use hierarchical or simple branch change with auto_save=True
                if use_hierarchy:
                    branch_success = self.change_user_branch_hierarchical(nova, user_request.branch_hierarchy, auto_save=True)
                else:
                    branch_success = self.change_user_branch(nova, user_request.new_branch, auto_save=True)
                
                if not branch_success:
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
                bank_user_changed = self.session_data.get('last_bank_user_change_performed', False)
                
                if not branch_changed and not bank_user_changed:
                    print("ℹ️ No changes needed - branch and bank user already set correctly")
            else:
                print("ℹ️ No changes requested (neither role nor branch)")

            # Determine the effective new branch for logging
            effective_new_branch = user_request.new_branch or "unchanged"
            if user_request.branch_hierarchy:
                effective_new_branch = user_request.branch_hierarchy[-1]  # Use final level from hierarchy

            # Determine if any changes were actually made
            role_changed = self.session_data.get('last_role_change_performed', False)
            branch_changed = self.session_data.get('last_branch_change_performed', False)
            bank_user_changed = self.session_data.get('last_bank_user_change_performed', False)
            
            # Create appropriate status message
            if role_requested and branch_requested:
                changed_items = []
                if role_changed: changed_items.append("role")
                if branch_changed: changed_items.append("branch")
                if bank_user_changed: changed_items.append("bank user")
                
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
                changed_items = []
                if branch_changed: changed_items.append("branch")
                if bank_user_changed: changed_items.append("bank user")
                
                if changed_items:
                    status = f"success - {' and '.join(changed_items)} updated"
                else:
                    status = "success - branch and bank user already correct"
            else:
                status = "success - no changes requested"

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
        """
        # Load configuration
        try:
            config = self.load_input_config(input_file)
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return False

        # Determine password precedence: config > passed param > prompt
        admin_password = config.admin_credentials.password or password
        if not admin_password:
            admin_password = getpass.getpass(f"Enter password for {config.admin_credentials.username}: ")

        success_count = 0

        # Parallel isolated mode
        if per_user_session and parallel_workers and parallel_workers > 1:
            print(f"⚙️ Parallel mode: {parallel_workers} workers (isolated sessions)")
            lock = threading.Lock()

            def worker(user_request: UserChangeRequest) -> RoleChangeResult:
                local_changer = CSPAdminRoleAndBranchChanger("", self.nova_act_api_key)  # independent session data
                for attempt in range(1, start_retries + 1):
                    try:
                        with NovaAct(starting_page=config.admin_credentials.csp_admin_url,
                                     headless=False, ignore_https_errors=True, 
                                     nova_act_api_key=local_changer.nova_act_api_key) as nova:
                            if not local_changer.login(nova, config.admin_credentials.username, admin_password):
                                return RoleChangeResult(
                                    user_email=user_request.target_user,
                                    new_role=user_request.new_role or "unchanged",
                                    new_branch=user_request.new_branch or "unchanged",
                                    status="failed - login failed",
                                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                                )
                            if not local_changer.navigate_to_user_management(nova):
                                return RoleChangeResult(
                                    user_email=user_request.target_user,
                                    new_role=user_request.new_role or "unchanged",
                                    new_branch=user_request.new_branch or "unchanged",
                                    status="failed - navigation failed",
                                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                                )
                            local_changer.process_single_user(nova, user_request)
                            return local_changer.results[-1]
                    except StartFailed as sf:
                        print(f"⚠️ StartFailed (attempt {attempt}/{start_retries}) for {user_request.target_user}: {sf}")
                        if attempt < start_retries:
                            time.sleep(2 * attempt)
                            continue
                        return RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status="failed - start timeout",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        )
                    except Exception as e:
                        return RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status=f"failed - {str(e)}",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        )

            with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
                future_map = {executor.submit(worker, u): u for u in config.users}
                for future in as_completed(future_map):
                    result_obj = future.result()
                    with lock:
                        self.results.append(result_obj)
                        if result_obj.status.startswith("success"):
                            success_count += 1
            total_users = len(config.users)
            print(f"\n📊 Parallel Batch Summary:")
            print(f"   Total users: {total_users}")
            print(f"   Successful: {success_count}")
            print(f"   Failed: {total_users - success_count}")
            if total_users:
                print(f"   Success rate: {(success_count/total_users)*100:.1f}%")
            self.save_results()
            return success_count == total_users

        if per_user_session:
            print("🔁 Using isolated browser session per user")
            for user_request in config.users:
                session_started = False
                for attempt in range(1, start_retries + 1):
                    try:
                        with NovaAct(starting_page=config.admin_credentials.csp_admin_url,
                                     headless=False, ignore_https_errors=True, 
                                     nova_act_api_key=self.nova_act_api_key) as nova:
                            session_started = True
                            if not self.login(nova, config.admin_credentials.username, admin_password):
                                self.results.append(RoleChangeResult(
                                    user_email=user_request.target_user,
                                    new_role=user_request.new_role or "unchanged",
                                    new_branch=user_request.new_branch or "unchanged",
                                    status="failed - login failed",
                                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                                ))
                                break
                            if not self.navigate_to_user_management(nova):
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
                            break
                    except StartFailed as sf:
                        print(f"⚠️ StartFailed (attempt {attempt}/{start_retries}) for {user_request.target_user}: {sf}")
                        if attempt < start_retries:
                            time.sleep(2 * attempt)
                            continue
                        self.results.append(RoleChangeResult(
                            user_email=user_request.target_user,
                            new_role=user_request.new_role or "unchanged",
                            new_branch=user_request.new_branch or "unchanged",
                            status="failed - start timeout",
                            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                        ))
                    except Exception as e:
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
            with NovaAct(starting_page=config.admin_credentials.csp_admin_url,
                         headless=False, ignore_https_errors=True, 
                         nova_act_api_key=self.nova_act_api_key) as nova:
                try:
                    if not self.login(nova, config.admin_credentials.username, admin_password):
                        self.save_results()
                        return False
                    if not self.navigate_to_user_management(nova):
                        self.save_results()
                        return False
                    for user_request in config.users:
                        if self.process_single_user(nova, user_request):
                            success_count += 1
                        time.sleep(1)
                except Exception as e:
                    print(f"❌ Batch processing error: {e}")

        total_users = len(config.users)
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
                "new_branch": "branch_001"
            },
            {
                "target_user": "user2@example.com",
                "new_role": "employee", 
                "new_branch": "branch_002",
                "branch_hierarchy": ["VIB Bank", "North", "002_HA NOI"]
            },
            {
                "target_user": "user3@example.com",
                "new_role": "supervisor",
                "branch_hierarchy": ["VIB Bank", "South", "005_HO CHI MINH"]
            }
        ]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Sample input file created: {filename}")
    print("💡 Note: Use 'branch_hierarchy' for hierarchical navigation or 'new_branch' for simple branch selection")


def main(
    input_file: str,
    password: str = None,
    per_user_session: bool = True,
    parallel_workers: int = 0,
    start_retries: int = 2,
    nova_act_api_key: str = None
):
    """
    Execute CSP admin role and branch change automation from JSON input file.
    
    Args:
        input_file: Path to JSON file containing user change requests
        password: Admin password (will prompt if not provided)
        per_user_session: Launch a new browser session per user for isolation (default True)
        nova_act_api_key: Nova Act API key (if not provided, will use environment variable)
    """
    
    if not input_file:
        print("Error: Please provide an input file")
        print("Usage: python -m nova_act.samples.vib_csp_automation.csp_admin_change_role_and_branch --input_file input.json")
        return
    
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        print("You can create a sample input file using the create_sample_input_file() function")
        return
    
    # Get Nova Act API key from parameter or configuration
    if not nova_act_api_key:
        try:
            nova_act_api_key = get_nova_act_api_key()
            print("✅ Using Nova Act API key from configuration")
        except Exception as e:
            print(f"❌ Error getting Nova Act API key: {e}")
            return
    
    print(f"🚀 Starting CSP Admin Role and Branch Change Automation")
    print(f"� Input file: {input_file}")
    print("=" * 50)
    
    # Create and run the automation
    changer = CSPAdminRoleAndBranchChanger("", nova_act_api_key)  # URL will be loaded from config
    success = changer.run_batch(input_file, password, per_user_session=per_user_session, parallel_workers=parallel_workers, start_retries=start_retries)
    
    if success:
        print("\n✅ All users processed successfully!")
    else:
        print("\n⚠️ Some users failed to process. Check results file for details.")


if __name__ == "__main__":
    import fire
    fire.Fire(main)
