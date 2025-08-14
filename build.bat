@echo off
REM Build script for AI Automation Application with NovaAct and Playwright
REM This script will create executable files using PyInstaller with full Playwright support

echo 🚀 Building AI Automation Application with Playwright...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python first.
    pause
    exit /b 1
)

REM Check for existing virtual environments and use the appropriate one
if exist "nova_act_env" (
    echo 🔧 Using existing nova_act_env virtual environment...
    call nova_act_env\Scripts\activate.bat
) else if exist "venv" (
    echo � Using existing venv virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo �📦 Creating new virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install or upgrade pip
echo 📦 Upgrading pip...
pip install --upgrade pip

REM Install requirements first
echo 📦 Installing Python requirements...
pip install -r requirements.txt

REM Install Playwright browsers (critical for NovaAct)
echo 🌐 Installing Playwright browsers (this may take a few minutes)...
playwright install chromium

REM Verify Playwright installation
echo ✅ Verifying Playwright installation...
python -c "from playwright.sync_api import sync_playwright; import sys; p = sync_playwright(); browser = p.start().chromium.launch(headless=True); browser.close(); p.stop(); print('✅ Playwright browsers installed successfully')" 2>nul
if errorlevel 1 (
    echo ❌ Playwright verification failed. Build cannot continue.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing PyInstaller...
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
echo 🔨 Building executable with Playwright support...
echo 📋 PyInstaller will include:
echo    - NovaAct package and artifacts
echo    - Playwright drivers and browsers
echo    - All Python dependencies
echo    - Configuration files
echo.

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
    
    REM Create a simple test script to verify the build
    echo 🧪 Creating build verification script...
    (
        echo #!/usr/bin/env python3
        echo import sys
        echo import os
        echo.
        echo print("🧪 Testing built application dependencies..."^)
        echo.
        echo try:
        echo     import nova_act
        echo     print("✅ NovaAct import successful"^)
        echo except ImportError as e:
        echo     print(f"❌ NovaAct import failed: {e}"^)
        echo     sys.exit(1^)
        echo.
        echo try:
        echo     from playwright.sync_api import sync_playwright
        echo     print("✅ Playwright import successful"^)
        echo except ImportError as e:
        echo     print(f"❌ Playwright import failed: {e}"^)
        echo     sys.exit(1^)
        echo.
        echo try:
        echo     with sync_playwright(^) as p:
        echo         print("✅ Playwright context created"^)
        echo         browser = p.chromium.launch(headless=True^)
        echo         print("✅ Chromium browser launched"^)
        echo         browser.close(^)
        echo         print("✅ Browser closed successfully"^)
        echo except Exception as e:
        echo     print(f"❌ Playwright browser test failed: {e}"^)
        echo     sys.exit(1^)
        echo.
        echo print("🎉 All tests passed! Built application should work correctly."^)
    ) > "dist\test_build.py"

    REM Create launch script for the built application
    echo 🚀 Creating launch script...
    (
        echo @echo off
        echo.
        echo REM Startup script for AI Automation App
        echo REM This ensures Playwright browsers are available before running the main application
        echo.
        echo set "SCRIPT_DIR=%%~dp0"
        echo set "APP_NAME=ai_automation_app.exe"
        echo.
        echo echo � Starting AI Automation Application...
        echo.
        echo REM Check if this is the first run by looking for a marker file
        echo set "FIRST_RUN_MARKER=%%SCRIPT_DIR%%.playwright_setup_complete"
        echo.
        echo if not exist "%%FIRST_RUN_MARKER%%" (
        echo     echo 🌐 First run detected - setting up Playwright browsers...
        echo     echo ⏳ This may take a few minutes to download browser binaries...
        echo     
        echo     REM Check if playwright command is available
        echo     playwright install chromium ^>nul 2^>^&1
        echo     if errorlevel 0 (
        echo         echo ✅ Playwright browsers installed successfully
        echo         echo. ^> "%%FIRST_RUN_MARKER%%"
        echo     ^) else (
        echo         echo ❌ Failed to install Playwright browsers
        echo         echo 💡 You may need to run this manually: playwright install chromium
        echo         pause
        echo     ^)
        echo     echo.
        echo ^)
        echo.
        echo REM Run the main application
        echo echo 🎯 Launching AI Automation Application...
        echo "%%SCRIPT_DIR%%%%APP_NAME%%" %%*
        echo.
        echo REM Capture the exit code
        echo set EXIT_CODE=%%ERRORLEVEL%%
        echo.
        echo if not %%EXIT_CODE%% == 0 (
        echo     echo.
        echo     echo ❌ Application exited with error code: %%EXIT_CODE%%
        echo     echo.
        echo     echo 🔧 Troubleshooting tips:
        echo     echo    1. Ensure Playwright browsers are installed: playwright install chromium
        echo     echo    2. Check that input.json is properly configured
        echo     echo    3. Verify network connectivity to the CSP portal
        echo     echo    4. Try running from a terminal for more detailed error messages
        echo     echo.
        echo ^)
        echo.
        echo exit /b %%EXIT_CODE%%
    ) > "dist\launch_app.bat"
    
    echo 📁 Executable file location:
    dir dist\
    echo.
    echo 🎉 Build completed successfully!
    echo.
    echo 🧪 To test the build:
    echo    cd dist ^&^& python test_build.py
    echo.
    echo 🚀 To run your application:
    echo    dist\ai_automation_app.exe
    echo    or use: dist\launch_app.bat
    echo.
    for %%F in (dist\ai_automation_app.exe) do echo 📦 File size: %%~zF bytes
    echo.
    echo 💡 Important notes:
    echo    - This build includes Playwright browsers
    echo    - The executable should work on systems without Python
    echo    - Make sure to copy both the executable and input.json
    echo    - For deployment, the entire dist/ folder may be needed
    
) else (
    echo ❌ Build failed!
    echo 💡 Common issues:
    echo    - Playwright browsers not installed properly
    echo    - Missing Python dependencies
    echo    - Insufficient disk space for browsers
    echo.
    echo 🔧 Try running: playwright install chromium
    pause
    exit /b 1
)

pause
