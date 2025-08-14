@echo off
REM Build script for Simple Python Application on Windows
REM This script will create executable files using PyInstaller

echo 🚀 Building Simple Python Application...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python first.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo 📦 PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Clean previous builds
if exist "build" (
    echo 🧹 Cleaning previous build...
    rmdir /s /q build
)

if exist "dist" (
    echo 🧹 Cleaning previous dist...
    rmdir /s /q dist
)

REM Build the application
echo 🔨 Building executable...
pyinstaller ai_automation_app.spec

REM Check if build was successful
if errorlevel 0 (
    echo ✅ Build successful!
    
    REM Copy input.json to dist directory
    echo 📋 Copying input.json to distribution directory...
    if exist "src\csp\input.json" (
        copy "src\csp\input.json" "dist\"
        echo ✅ input.json copied successfully
    ) else (
        echo ⚠️  input.json not found in src\csp\ - you can add it later
    )
    
    echo 📁 Executable file location:
    dir dist\
    echo.
    echo 🎉 You can now run your application:
    echo    dist\ai_automation_app.exe
    echo.
    echo 💡 Tip: You can copy this file and input.json to any Windows computer and run it without Python installed!
) else (
    echo ❌ Build failed!
    pause
    exit /b 1
)

pause
