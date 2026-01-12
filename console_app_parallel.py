#!/usr/bin/env python3
import sys
import os

# CRITICAL: Set Playwright browsers path BEFORE any imports
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    app_dir = os.path.dirname(sys.executable)
    playwright_browsers = os.path.join(app_dir, 'ms-playwright')
    if os.path.exists(playwright_browsers):
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = playwright_browsers
        print(f"📦 Using bundled Playwright browsers from: {playwright_browsers}")
    else:
        print(f"⚠️  WARNING: Browsers not found at: {playwright_browsers}")
        print(f"    App may fail if Playwright is not installed globally")

# Skip Playwright auto-install (browsers already exist)
os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '1'

# Now safe to import other modules
import json
from dotenv import load_dotenv

load_dotenv()


def get_input_file_path():
    """Get input.json path"""
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_path, "input.json")


def load_and_display_config(input_path):
    """Load and display config from input.json"""
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

        return True
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error loading config: {e}")
        return False


def run_automation_parallel(input_path, max_workers=3):
    """Run the parallel automation"""
    try:
        print("\n" + "=" * 60)
        print(f"🚀 Starting PARALLEL automation (max {max_workers} workers)...")
        print("=" * 60)

        from src.features.csp.csp_admin_parallel import main as csp_parallel_main
        success = csp_parallel_main(input_file=input_path, max_workers=max_workers)

        print("\n" + "=" * 60)
        if success:
            print("✅ Parallel automation completed successfully!")
        else:
            print("⚠️  Parallel automation completed with some errors")
        print("=" * 60)
        return success

    except KeyboardInterrupt:
        print("\n\n⚠️  Automation interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Automation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_menu():
    """Show menu options"""
    print("\n" + "=" * 60)
    print("📋 MENU")
    print("=" * 60)
    print("  [r] Run automation again")
    print("  [l] Reload input.json and run")
    print("  [w] Change max workers")
    print("  [q] Quit")
    print("=" * 60)


def main():
    """Main function - runs continuously"""
    print("=" * 60)
    print("🚀 CSP ADMIN AUTOMATION - PARALLEL MODE")
    print("=" * 60)
    print("💡 Process multiple users concurrently (default: 3 workers)")
    print("💡 App will keep running until you choose to quit")

    input_path = get_input_file_path()

    # Check input file exists
    if not os.path.exists(input_path):
        print(f"\n❌ File not found: {input_path}")
        print("💡 Place input.json in the same folder as this app")
        input("\nPress Enter to exit...")
        return

    # Initial config load
    if not load_and_display_config(input_path):
        input("\nPress Enter to exit...")
        return

    # Default max workers
    max_workers = 3

    # Main loop
    first_run = True
    while True:
        try:
            if first_run:
                # First run - ask for confirmation and max workers
                print(f"\n⚠️  This will run browser automation in PARALLEL mode")
                print(f"💡 Current max workers: {max_workers}")

                # Ask if want to change max workers
                change_workers = input("Change max workers? (y/N): ").strip().lower()
                if change_workers == 'y':
                    try:
                        new_workers = int(input(f"Enter max workers (1-10, current: {max_workers}): ").strip())
                        if 1 <= new_workers <= 10:
                            max_workers = new_workers
                            print(f"✅ Max workers set to: {max_workers}")
                        else:
                            print("⚠️  Invalid value. Using default: 3")
                    except ValueError:
                        print("⚠️  Invalid input. Using default: 3")

                confirm = input("Start? (y/N): ").strip().lower()

                if confirm not in ['y', 'yes']:
                    print("❌ Cancelled")
                    break

                first_run = False

            # Run automation
            run_automation_parallel(input_path, max_workers)

            # Show menu and get user choice
            while True:
                show_menu()
                choice = input("\nYour choice: ").strip().lower()

                if choice == 'r':
                    # Run again
                    print(f"\n🔄 Running again with same config (max workers: {max_workers})...")
                    break
                elif choice == 'l':
                    # Reload config
                    print("\n🔄 Reloading input.json...")
                    if load_and_display_config(input_path):
                        print("✅ Config reloaded successfully")
                        break
                    else:
                        print("❌ Failed to reload config. Using previous config.")
                        continue
                elif choice == 'w':
                    # Change max workers
                    try:
                        new_workers = int(input(f"Enter max workers (1-10, current: {max_workers}): ").strip())
                        if 1 <= new_workers <= 10:
                            max_workers = new_workers
                            print(f"✅ Max workers set to: {max_workers}")
                        else:
                            print("⚠️  Invalid value. Must be between 1-10")
                    except ValueError:
                        print("⚠️  Invalid input. Must be a number")
                    continue
                elif choice == 'q':
                    # Quit
                    print("\n👋 Exiting...")
                    return
                else:
                    print("❌ Invalid choice. Please enter 'r', 'l', 'w', or 'q'")
                    continue

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            print("👋 Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

            # Ask if continue
            cont = input("\nContinue? (y/N): ").strip().lower()
            if cont not in ['y', 'yes']:
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    finally:
        # Keep terminal open after execution
        input("\nPress Enter to exit...")
