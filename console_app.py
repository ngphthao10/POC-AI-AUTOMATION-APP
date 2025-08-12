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
    print("=" * 60)
    print("    🐍 AI AUTOMATION APPLICATION 🐍")
    print("    Console-based Utilities")
    print("=" * 60)
    print()

def print_menu():
    """Print main menu"""
    print("📋 MAIN MENU:")
    print("1. Say Hello")
    print("2. Show Current Time")
    print("3. Show System Information")
    print("4. Simple Calculator")
    print("5. Text Reverser")
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
