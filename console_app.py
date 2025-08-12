#!/usr/bin/env python3
"""
AI Automation Application
A console-based automation application with various utilities
"""

import sys
import os
import datetime
import platform

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
    print("1. Say Hello")
    print("2. Show Current Time")
    print("3. Show System Information")
    print("4. Simple Calculator")
    print("5. Text Reverser")
    print("6. Exit")
    print("-" * 30)

def say_hello():
    """Get user name and say hello"""
    print("\n👋 HELLO FUNCTION")
    print("-" * 20)
    name = input("Enter your name: ").strip()
    if name:
        print(f"\nHello, {name}! 🎉")
        print("Nice to meet you!")
    else:
        print("Hello, stranger! 👋")
    input("\nPress Enter to continue...")

def show_time():
    """Show current date and time"""
    print("\n⏰ CURRENT TIME")
    print("-" * 20)
    now = datetime.datetime.now()
    print(f"Date: {now.strftime('%Y-%m-%d')}")
    print(f"Time: {now.strftime('%H:%M:%S')}")
    print(f"Day of week: {now.strftime('%A')}")
    input("\nPress Enter to continue...")

def show_system_info():
    """Show system information"""
    print("\n💻 SYSTEM INFORMATION")
    print("-" * 25)
    print(f"Platform: {platform.system()}")
    print(f"Platform Release: {platform.release()}")
    print(f"Platform Version: {platform.version()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Current Directory: {os.getcwd()}")
    input("\nPress Enter to continue...")

def calculator():
    """Simple calculator function"""
    print("\n🔢 SIMPLE CALCULATOR")
    print("-" * 20)
    try:
        num1 = float(input("Enter first number: "))
        operator = input("Enter operator (+, -, *, /): ").strip()
        num2 = float(input("Enter second number: "))
        
        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            if num2 != 0:
                result = num1 / num2
            else:
                print("Error: Division by zero!")
                input("\nPress Enter to continue...")
                return
        else:
            print("Error: Invalid operator!")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nResult: {num1} {operator} {num2} = {result}")
        
    except ValueError:
        print("Error: Please enter valid numbers!")
    
    input("\nPress Enter to continue...")

def text_reverser():
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
                say_hello()
            elif choice == '2':
                show_time()
            elif choice == '3':
                show_system_info()
            elif choice == '4':
                calculator()
            elif choice == '5':
                text_reverser()
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
