#!/usr/bin/env python3
"""
AI Automation Application
A console-based automation application with various utilities
"""

import sys
import os

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print application header"""
    print("=" * 50)
    print("    🤖 AI AUTOMATION APPLICATION 🤖")
    print("=" * 50)
    print()

def print_menu():
    """Print main menu"""
    print("📋 MENU:")
    print("6. Exit")
    print("-" * 30)
    """Reverse text function"""
    print("\n🔄 TEXT REVERSER")
    print("-" * 20)
    text = input("Enter text to reverse: ")
    if text:
        reversed_text = text[::-1]
        print(f"\nOriginal: {text}")
        print(f"Reversed: {reversed_text}")
    else:
        print("No text entered!")
    input("\nPress Enter to continue...")

def main():
    """Main function"""
    try:
        while True:
            clear_screen()
            print_header()
            print_menu()
            
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                print("\n👋 Hi! Thanks for using the app!")
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
