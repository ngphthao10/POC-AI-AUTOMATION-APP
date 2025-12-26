from nova_act import NovaAct, BOOL_SCHEMA
from typing import List
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.logger import setup_logger

logger = setup_logger(__name__)


class CSPPlaywrightHandler:
    """Fast handler using Playwright directly for CSP user updates."""

    def __init__(self, nova: NovaAct):
        self.nova = nova
        self.page = nova.page

    def click_roles_tab(self):
        """Click Roles tab."""
        print("  ➤ Opening Roles tab...")
        roles_tab = self.page.locator('a:has-text("Roles")').first
        roles_tab.click()
        time.sleep(2)

    def update_role(self, new_role: str):
        """Update role using Playwright."""
        print(f"👤 Updating role to: {new_role}")

        # Open dropdown
        print("  ➤ Opening role dropdown...")
        role_dropdown = self.page.locator('select').first
        role_dropdown.click()
        time.sleep(1)

        # Search role
        print(f"  ➤ Searching for role: {new_role}...")
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")
        self.page.keyboard.type(new_role, delay=100)
        time.sleep(1)

        # Select role
        print(f"  ➤ Selecting role...")
        self.page.keyboard.press("Enter")
        time.sleep(1)

        # Verify
        result = self.nova.act_get(
            f"Look at the FIRST Role field. Does it show '{new_role}'?",
            schema=BOOL_SCHEMA
        )
        if result.parsed_response:
            print(f"  ✅ Role updated to: {new_role}")
        else:
            print(f"  ⚠️ Role verification failed")

    def update_bank_user(self, bank: str, region: str, branch: str):
        """Update Bank User field."""
        print(f"🏦 Updating Bank User to: {branch}")

        # Click field
        print("  ➤ Opening Bank User selector...")
        bank_user_field = self.page.locator('input').first
        bank_user_field.click()
        time.sleep(1)

        # Select Bank
        print(f"  ➤ Selecting bank: {bank}...")
        self.page.locator(f'text="{bank}"').first.click()
        time.sleep(1)

        # Select Region
        print(f"  ➤ Selecting region: {region}...")
        self.page.locator(f'text="{region}"').first.click()
        time.sleep(1)

        # Search and select Branch
        print(f"  ➤ Selecting branch: {branch}...")
        self.page.keyboard.type(branch, delay=100)
        time.sleep(1)
        self.page.locator(f'text="{branch}"').first.click()
        time.sleep(1)

        # Confirm
        print("  ➤ Confirming selection...")
        self.page.locator('button:has-text("Select")').first.click()
        time.sleep(1)

        # Verify
        result = self.nova.act_get(
            f"Look at the Bank user field. Does it show '{branch}'?",
            schema=BOOL_SCHEMA
        )
        if result.parsed_response:
            print(f"  ✅ Bank user updated to: {branch}")
        else:
            print(f"  ⚠️ Bank user verification failed")

    def update_scope(self, bank: str, region: str, branch: str):
        """Update Scope field by setting data-content attribute."""
        print(f"🎯 Updating Scope to: {branch}")

        scope_path = f"{bank} / {region} / {branch}"

        # Set data-content attribute directly
        scope_input = self.page.locator('input[placeholder="Select scope..."]').first
        scope_input.evaluate(f'element => element.setAttribute("data-content", "{scope_path}")')
        time.sleep(0.5)

        # Verify
        result = self.nova.act_get(
            f"Look at the Scope field. Does it show '{scope_path}'?",
            schema=BOOL_SCHEMA
        )
        if result.parsed_response:
            print(f"  ✅ Scope updated to: {branch}")
        else:
            print(f"  ⚠️ Scope verification failed")

    def update_branch(self, bank: str, region: str, branch: str):
        """Update both Bank User and Scope."""
        self.update_bank_user(bank, region, branch)
        self.update_scope(bank, region, branch)

    def save_changes(self):
        """Save changes."""
        print("💾 Saving changes...")
        self.page.locator('button:has-text("Save")').first.click()
        time.sleep(2)
        print("✅ Changes saved!")
