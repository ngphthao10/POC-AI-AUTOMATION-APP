#!/usr/bin/env python3
"""
AI Automation Application
A console-based automation application with various utilities
"""

import sys
import os
import json
from pathlib import Path

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print application header"""
    print("=" * 60)
    print("    🐍 AI AUTOMATION APPLICATION 🐍")
    print("    Console-based Utilities")
    print("=" * 60)
    print()

def print_menu():
    """Print main menu"""
    print("📋 MAIN MENU:")
    print("1. Say Hello")
    print("2. CSP Admin - Change Role and Branch")
    print("6. Exit")
    print("-" * 40)

def say_hello():
    """Say hello function"""
    print("\n👋 HELLO!")
    print("-" * 10)
    name = input("What's your name? ").strip()
    if name:
        print(f"\nHello, {name}! Welcome to the Simple Python Application!")
        print("This app includes various console utilities for your convenience.")
    else:
        print("\nHello there! Thanks for using our simple console app!")
    input("\nPress Enter to continue...")

def csp_admin_change_role_and_branch():
    """CSP Admin - Change Role and Branch functionality"""
    print("\n🏢 CSP ADMIN - CHANGE ROLE AND BRANCH")
    print("=" * 45)
    print("This feature allows you to change user roles and branches in the CSP system.")
    print("\nNote: This runs the actual automation with browser control.")
    print("\nFeatures:")
    print("• Change user roles (CSP-RB-TELLER, CSP_Inquiry, etc.)")
    print("• Update branch assignments")
    print("• Support for hierarchical branch navigation")
    print("• Batch processing from JSON input files")
    
    print("\n📂 Available input file: src/csp/input.json")
    print("\nTo run the full automation:")
    print("python -m src.csp.csp_admin_change_role_and_branch --input_file src/csp/input.json")
    
    print("\n⚠️  Important Notes:")
    print("• Requires valid admin credentials in the input file")
    print("• Uses browser automation (NovaAct) for web interactions")
    print("• Uses isolated browser sessions for reliability")
    print("• Results are saved to timestamped JSON files")
    
    while True:
        print("\n📋 CSP Admin Options:")
        print("1. View sample input format")
        print("2. View current input file")
        print("3. Run CSP automation")
        print("4. Back to main menu")
        
        choice = input("\nChoose an option (1-4): ").strip()
        
        if choice == '1':
            show_sample_input_format()
        elif choice == '2':
            show_current_input_file()
        elif choice == '3':
            demo_automation_run()
        elif choice == '4':
            break
        else:
            print("❌ Invalid choice! Please try again.")
            input("Press Enter to continue...")

def show_sample_input_format():
    """Show sample input format for CSP automation"""
    print("\n📄 SAMPLE INPUT FORMAT:")
    print("-" * 30)
    sample = '''{
  "admin_credentials": {
    "username": "your_admin_username",
    "password": "your_admin_password",
    "csp_admin_url": "https://your-csp-portal.com/portal/users/list"
  },
  "users": [
    {
      "target_user": "user1@example.com",
      "new_role": "CSP-RB-TELLER",
      "new_branch": "002"
    },
    {
      "target_user": "user2@example.com",
      "new_role": "CSP_Inquiry",
      "branch_hierarchy": ["VIB Bank", "North", "003"]
    }
  ]
}'''
    print(sample)
    input("\nPress Enter to continue...")

def show_current_input_file():
    """Show current input file contents"""
    try:
        input_path = "src/csp/input.json"
        if os.path.exists(input_path):
            print(f"\n📄 CURRENT INPUT FILE: {input_path}")
            print("-" * 40)
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
        else:
            print(f"\n❌ Input file not found: {input_path}")
    except Exception as e:
        print(f"\n❌ Error reading input file: {e}")
    input("\nPress Enter to continue...")

def demo_automation_run():
    """Run actual CSP automation"""
    print("\n🚀 CSP ADMIN AUTOMATION")
    print("-" * 35)
    
    # Check if input file exists
    input_path = "src/csp/input.json"
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        print("Please ensure the input file exists with proper configuration.")
        input("\nPress Enter to continue...")
        return
    
    try:
        # Load and validate input file
        with open(input_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        print(f"✅ Loaded configuration from {input_path}")
        print(f"📊 Found {len(config_data.get('users', []))} users to process")
        
        # Show configuration summary
        admin_url = config_data.get('admin_credentials', {}).get('csp_admin_url', 'Not specified')
        admin_user = config_data.get('admin_credentials', {}).get('username', 'Not specified')
        
        print(f"\n📋 Configuration Summary:")
        print(f"   Admin URL: {admin_url}")
        print(f"   Admin User: {admin_user}")
        print(f"   Users to process: {len(config_data.get('users', []))}")
        
        # Show users list
        users = config_data.get('users', [])
        if users:
            print(f"\n👥 Users to process:")
            for i, user in enumerate(users, 1):
                target_user = user.get('target_user', 'Unknown')
                new_role = user.get('new_role') or 'No change'
                new_branch = user.get('new_branch') or 'No change'
                branch_hierarchy = user.get('branch_hierarchy')
                
                print(f"   {i}. {target_user}")
                print(f"      Role: {new_role}")
                if branch_hierarchy:
                    print(f"      Branch Hierarchy: {' → '.join(branch_hierarchy)}")
                else:
                    print(f"      Branch: {new_branch}")
        
        # Ask for confirmation
        print(f"\n⚠️  IMPORTANT:")
        print("• This will perform actual automation using browser automation")
        print("• Make sure you have the required dependencies installed")
        print("• Ensure the CSP admin portal is accessible")
        print("• This may take several minutes to complete")
        
        confirm = input("\nDo you want to proceed with the automation? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            print("\n🔄 Starting automation...")
            run_actual_csp_automation(input_path)
        else:
            print("❌ Automation cancelled by user.")
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format in {input_path}: {e}")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
    
    input("\nPress Enter to continue...")

def run_actual_csp_automation(input_file: str):
    """Run the actual CSP automation"""
    try:
        print("📦 Importing CSP automation module...")
        
        # Try to import the CSP module
        try:
            from src.csp.csp_admin_change_role_and_branch import CSPAdminRoleAndBranchChanger
            print("✅ CSP module imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import CSP module: {e}")
            print("Make sure all dependencies are installed:")
            print("   pip install nova-act fire pydantic")
            return
        
        # Create and run the automation
        print("🚀 Initializing CSP automation...")
        changer = CSPAdminRoleAndBranchChanger("")
        
        # Ask for parallel workers option
        print("\n⚙️  Automation Configuration:")
        print("Using isolated sessions (each user gets a fresh browser session)")
        
        parallel_workers = 1
        try:
            workers_input = input("Number of parallel workers (1-4, default=1): ").strip()
            if workers_input:
                parallel_workers = max(1, min(4, int(workers_input)))
        except ValueError:
            parallel_workers = 1
        
        print(f"\n🔧 Configuration:")
        print(f"   Session mode: Isolated (recommended)")
        print(f"   Parallel workers: {parallel_workers}")
        
        print(f"\n🎯 Starting automation...")
        print("=" * 50)
        
        # Run the automation with isolated sessions
        success = changer.run_batch(
            input_file=input_file,
            per_user_session=True,
            parallel_workers=parallel_workers if parallel_workers > 1 else None
        )
        
        print("=" * 50)
        if success:
            print("✅ Automation completed successfully!")
            print("📄 Results have been saved to a timestamped JSON file.")
        else:
            print("⚠️  Automation completed with some failures.")
            print("📄 Check the results file for detailed information.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Automation interrupted by user")
    except Exception as e:
        print(f"\n❌ Automation error: {e}")
        print("Please check your configuration and try again.")

def main():
    """Main function"""
    try:
        while True:
            clear_screen()
            print_header()
            print_menu()
            
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                say_hello()
            elif choice == '2':
                csp_admin_change_role_and_branch()
            elif choice == '6':
                print("\n👋 Goodbye! Thanks for using the app!")
                break
            else:
                print("\n❌ Invalid choice! Please try again.")
                input("Press Enter to continue...")
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using the app!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
