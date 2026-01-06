#!/usr/bin/env python3
import sys
import os
import json
from dotenv import load_dotenv

# Set Playwright browsers path for portable distribution
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    app_dir = os.path.dirname(sys.executable)
    playwright_browsers = os.path.join(app_dir, 'ms-playwright')
    if os.path.exists(playwright_browsers):
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = playwright_browsers
        print(f"📦 Using bundled Playwright browsers from: {playwright_browsers}")

load_dotenv()


def get_input_file_path():
    """Get input.json path"""
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_path, "input.json")


def main():
    """Main function"""
    print("=" * 60)
    print("🚀 CSP ADMIN AUTOMATION")
    print("=" * 60)

    input_path = get_input_file_path()

    # Check input file
    if not os.path.exists(input_path):
        print(f"\n❌ File not found: {input_path}")
        print("💡 Place input.json in the same folder as this app")
        input("\nPress Enter to exit...")
        return

    # Load and display config
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        users = config.get('users', [])
        admin = config.get('admin_credentials', {}).get('username', 'N/A')

        print(f"\n📂 Config file: {input_path}")
        print(f"👤 Admin: {admin}")
        print(f"👥 Users to process: {len(users)}")

        if users:
            print(f"\n📋 User list:")
            for i, user in enumerate(users, 1):
                target = user.get('target_user', 'Unknown')
                role = user.get('new_role', 'No change')
                branch = user.get('branch_hierarchy', [])
                branch_code = branch[-1] if branch else 'N/A'
                print(f"   {i}. {target} → Branch: {branch_code} | Role: {role}")

        # Confirm
        print(f"\n⚠️  This will run browser automation")
        confirm = input("Continue? (y/N): ").strip().lower()

        if confirm not in ['y', 'yes']:
            print("❌ Cancelled")
            return

        # Run automation
        print("\n" + "=" * 60)
        from src.features.csp.csp_admin import main as csp_main
        success = csp_main(input_file=input_path)

        print("\n" + "=" * 60)
        if success:
            print("✅ Completed successfully!")
        else:
            print("⚠️  Completed with errors")
        print("=" * 60)

    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    finally:
        # Keep terminal open after execution
        input("\nPress Enter to exit...")
